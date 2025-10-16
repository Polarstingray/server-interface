import subprocess
import time

class ServerAPI:
    @staticmethod
    def response(status_code, message, data=None):
        return {
            "status": status_code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def list_vms() :
        """
        retuns dictionary with vm name keys and vm {id : , name : , state : } as value
        """
        payload = {}
        result, success = run_command('virsh list --all')
        if not success:
            return ServerAPI.response(1, "Failed to list VMs", result)

        lines = result.stdout.strip().split('\n')[2:]
        for line in lines :
            parts = line.split(None, 2)
            if (len(parts) == 3) :
                vm_id, name, state = parts
            payload[name] = {'id' : vm_id, 'name' : name, 'state' : state}   
        return ServerAPI.response(0, "list of vms", payload)

    @staticmethod
    def isVM(name) :
        vms = ServerAPI.list_vms()
        if vms["status"] != 0 :
            return False
        # return name in    
        return name in vms["data"].keys()

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
            print(name)
            return ServerAPI.response(1, "invalid vm name", None)
        result, success = run_command(['virsh', 'start', name])
        if not success:
            return ServerAPI.response(1, "Failed to start VM", result)
        return ServerAPI.response(0, f'started {name}', result.stdout.strip())


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
        return ServerAPI.response(0, f'rebooted {name}', result.stdout.strip())

    @staticmethod
    def stop_vm(name) :
        """
        retuns output from stopping vm
        """
        
        if (not ServerAPI.isVM(name)) :
            return ServerAPI.response(1, "invalid vm name", None)

        result, success = run_command(f'virsh shutdown {name}')
        if not success:
            return ServerAPI.response(1, "Failed to stop VM: run_command utility failed", result)
            # Wait for the VM to shut off
        for _ in range(10) :
            state = ServerAPI.vm_state(name)["data"]
            if state == "shut off" :
                return ServerAPI.response(0, f'stopped {name}', result.stdout.strip())
            time.sleep(1)
        return ServerAPI.response(1, "Failed to stop VM: Timeout", result.stdout.strip())

    @staticmethod
    def create_vm(data) :
        """
        creates a vm from an xml file
        """
        result, success = run_command(f'echo {data["name"]} {data["memory"]} {data["vcpus"]} {data["os"]} {data["network"]} {data["disk_path"]} {data["iso"]}')
        if not success:
            return ServerAPI.response(1, "Failed to create VM", result)
        return ServerAPI.response(0, f'created {data["name"]}', result.stdout.strip())

    @staticmethod
    def run_cmd(cmd, timeout=30):
        """
        runs a command and returns (result, success)
        result is subprocess.CompletedProcess on success
        result is error dictionary on failure
        success is boolean
        """
        result, success = run_command(cmd, timeout)
        if not success:
            return ServerAPI.response(1, "Command failed", result)
        return ServerAPI.response(0, "Command succeeded", result.stdout.strip())

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