import subprocess
import time

class ServerAPI:
    @staticmethod
    def response(status_code, message, data=None):
        return {
            "status_code": status_code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def list_vms() :
        """
        retuns dictionary with vm name keys and vm {id : , name : , state : } as value
        """
        result = {}
        cmd, success = run_command('virsh list --all')
        if not success:
            return ServerAPI.response(1, "Failed to list VMs", cmd)
    
        lines = cmd.stdout.strip().split('\n')[2:]
        for line in lines :
            parts = line.split(None, 2)
            if (len(parts) == 3) :
                vm_id, name, state = parts
                result[name] = {'id' : vm_id, 'name' : name, 'state' : state}   
        return ServerAPI.response(0, "list of vms", result)
    
    @staticmethod
    def isVM(name) :
        vms = ServerAPI.list_vms()
        return name in vms
    
    @staticmethod
    def vm_state(name) :
        """
        retuns state of vm
        """
        if (not ServerAPI.isVM(name)) :
            return ServerAPI.response(1, "invalid vm name", None)
        result, success = run_command(['virsh', 'domstate', name])
        if not success:
            return ServerAPI.response(1, "Failed to get VM state", result)
        return ServerAPI.response(0, "VM state", result.stdout.strip())

    @staticmethod
    def start_vm(name) :
        """
        retuns output from starting a vm
        """
        if (not ServerAPI.isVM(name)) :
            return ServerAPI.response(1, "invalid vm name", None)
        result, success = run_command(['virsh', 'start', name])
        if not success:
            return ServerAPI.response(1, "Failed to start VM", result)
        return ServerAPI.response(0, "VM started", result.stdout.strip())


    @staticmethod
    def reboot_vm(name) :
        """
        retuns output from rebooting a vm
        """
        if (not ServerAPI.isVM(name)) :
            return ServerAPI.response(1, "invalid vm name", None)
        result, success = run_command(f'virsh reboot {name}')
        if not success:
            return ServerAPI.response(1, "Failed to reboot VM", result)
        return ServerAPI.response(0, "VM rebooted", result.stdout.strip())

    @staticmethod
    def stop_vm(name) :
        """
        retuns output from stopping vm
        """
        
        if (not ServerAPI.isVM(name)) :
            return ServerAPI.response(1, "invalid vm name", None)

        result, success = run_command(f'virsh shutdown {name}')
        if not success:
            return ServerAPI.response(1, "Failed to stop VM", result)
            # Wait for the VM to shut off
        for _ in range(10) :
            state = run_command(f'virsh domstate {name}').stdout.strip()
            if state == "shut off" :
                return ServerAPI.response(0, "VM stopped", result.stdout.strip())
            time.sleep(1)
        return ServerAPI.response(1, "Failed to stop VM: Timeout", None)

def run_command(cmd, timeout=30):
        try:
            result = subprocess.run(
                cmd.split() if isinstance(cmd, str) else cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return result, True
        except subprocess.CalledProcessError as e:
            return {"error": f"Command failed: {e}", "stdout": e.stdout, "stderr": e.stderr}, False
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out", "stdout" : "Command timed out"}, False


if __name__ == "__main__":
    # vms = ServerAPI.list_vms()
    # print(vms) 


    pass