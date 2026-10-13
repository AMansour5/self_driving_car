import rclpy
from rclpy.node import Node
from rclpy.task import Future
from std_msgs.msg import String
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState
from control.services.MissionManager import MissionManager, Phase

class MissionManagerNode(Node):
    """
    The Supreme Orchestrator.
    Handles Lifecycle Management (Configure, Activate, Deactivate, Cleanup), 
    Drive2 Action goals, and Vision timeouts.
    """

    def __init__(self):
        super().__init__('mission_manager_node')
        self._log = self.get_logger()

        # 1. Mission Configurations
        self.manager = MissionManager()

        # 2. Setup Lifecycle Service Clients
        self.manual_client = self.create_client(ChangeState, '/manual_drive_node/change_state')
        self.auto_client = self.create_client(ChangeState, '/autonomous_drive_node/change_state')

        # 3. Setup Subscribers
        self.mode_sub = self.create_subscription(String, '/control_mode', self.mode_callback, 10)
        
        # 4. Execute Boot Sequence
        self._log.info("Waiting for drive nodes to come online...")
        self._timer = self.create_timer(0.1, self._timer_callback)
        self._execute_boot_sequence()

    def _timer_callback(self):
        # This can be used to periodically check the status of the mission manager or other tasks
        pass

    # LIFECYCLE ORCHESTRATION
    def _execute_boot_sequence(self):
        """
        Brings nodes from Unconfigured -> Inactive -> Active.
        """
        # Ensure services are available before sending requests
        self.manual_client.wait_for_service(timeout_sec=5.0)
        self.auto_client.wait_for_service(timeout_sec=5.0)
        self._log.info("Configuring drive Nodes (Loading YAMLs, Shared Memory, etc.)...")
        
        # 1. Send CONFIGURE to both (Moves them to 'Inactive')
        self._change_lifecycle_state(self.manual_client, Transition.TRANSITION_CONFIGURE, "ManualDrive")
        self._change_lifecycle_state(self.auto_client, Transition.TRANSITION_CONFIGURE, "AutoDrive")

        # 2. Automatically Activate Phase 1 (Manual)
        self._log.info("Boot sequence complete. Activating default Phase 1 (Manual).")
        self._change_lifecycle_state(self.manual_client, Transition.TRANSITION_ACTIVATE, "ManualDrive")

    def _execute_transition_to_manual(self):
        """Safely pauses Auto and spins up Manual."""
        self._log.info("Transitioning stack to MANUAL control...")
        
        # 1. Deactivate Autonomous Node (Active -> Inactive)
        self._change_lifecycle_state(self.auto_client, Transition.TRANSITION_DEACTIVATE, "AutoDrive")
        
        # 2. Activate Manual Node (Inactive -> Active)
        self._change_lifecycle_state(self.manual_client, Transition.TRANSITION_ACTIVATE, "ManualDrive")

    def _execute_transition_to_auto(self):
        """Safely pauses Manual, spins up Auto, and triggers Waypoint 1."""
        self._log.info("Transitioning stack to AUTONOMOUS control...")
        
        # 1. Deactivate Manual Node (Active -> Inactive)
        self._change_lifecycle_state(self.manual_client, Transition.TRANSITION_DEACTIVATE, "ManualDrive")
        # 2. Activate Autonomous Node (Inactive -> Active)
        self._change_lifecycle_state(self.auto_client, Transition.TRANSITION_ACTIVATE, "AutoDrive")

    def _execute_teardown_sequence(self):
        """
        Called on shutdown to completely free resources.
        Moves nodes from Active/Inactive -> Unconfigured.
        """
        self._log.info("Unconfiguring nodes to free shared memory and hardware locks...")
        
        # First ensure they are deactivated
        self._change_lifecycle_state(self.manual_client, Transition.TRANSITION_DEACTIVATE, "ManualDrive")
        self._change_lifecycle_state(self.auto_client, Transition.TRANSITION_DEACTIVATE, "AutoDrive")
        
        # Then Unconfigure (Cleanup)
        self._change_lifecycle_state(self.manual_client, Transition.TRANSITION_CLEANUP, "ManualDrive")
        self._change_lifecycle_state(self.auto_client, Transition.TRANSITION_CLEANUP, "AutoDrive")

    def _change_lifecycle_state(self, client: rclpy.client.Client, transition_id: int, node_label: str):
        """Helper to send standard ROS 2 lifecycle transition requests."""
        if not client.wait_for_service(timeout_sec=2.0):
            self._log.warn(f"Lifecycle service {client.srv_name} not available.")
            return

        req = ChangeState.Request()
        req.transition.id = transition_id
        
        # Send async so we don't block the orchestrator
        future = client.call_async(req)
        future.add_done_callback(lambda f: self._lifecycle_result_cb(f, node_label, transition_id))

    def _lifecycle_result_cb(self, future: Future, node_label: str, transition_id: int):
        """Handles the response from the lifecycle nodes."""
        try:
            response = future.result()
            transition_map = {
                Transition.TRANSITION_CONFIGURE: "Configured (Inactive)",
                Transition.TRANSITION_ACTIVATE: "Activated",
                Transition.TRANSITION_DEACTIVATE: "Deactivated (Inactive)",
                Transition.TRANSITION_CLEANUP: "Unconfigured (Cleaned Up)"
            }
            state_str = transition_map.get(transition_id, "Unknown State")

            if response.success:
                self._log.info(f"{node_label} successfully transitioned to: {state_str}.")
            else:
                self._log.error(f"{node_label} FAILED to transition to: {state_str}.")
        except Exception as e:
            self._log.error(f"Lifecycle service call failed for {node_label}: {e}")

    # CALLBACKS
    def mode_callback(self, msg: String):
        """Triggered by the GUI to change the operational phase."""
        try:
            requested_phase = msg.data.strip().lower()
            changed = self.manager.set_phase(requested_phase)
            
            if not changed:
                return # Ignore duplicate state commands

            if requested_phase == Phase.MANUAL.value:
                self._execute_transition_to_manual()
            elif requested_phase == Phase.AUTONOMOUS.value:
                self._execute_transition_to_auto()

        except Exception as e:
            self._log.error(f"Failed to process mission state request: {e}")

    def destroy_node(self):
        """Intercepts node destruction to Unconfigure the worker nodes."""
        # We do not send Lifecycle network calls here because during Ctrl+C, 
        # the ROS context is invalid and the target nodes are already dead.
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    try:
        node = MissionManagerNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal node error: {e}")
    finally:
        if 'node' in locals():
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()