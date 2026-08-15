import subprocess
import time
import os
import sys

def main():
    print("Starting Federated Learning Simulation...")
    
    # Path to scripts
    base_dir = os.path.dirname(__file__)
    server_script = os.path.join(base_dir, "fl", "server.py")
    client_script = os.path.join(base_dir, "fl", "client.py")
    
    # Ensure we use the current python interpreter (which should be the venv one)
    python_exec = sys.executable
    
    # Start server
    print("Starting server...")
    server_process = subprocess.Popen([python_exec, server_script])
    
    # Wait for server to start
    time.sleep(3)
    
    # Start clients
    client_processes = []
    for i in range(1, 5):
        print(f"Starting client {i}...")
        p = subprocess.Popen([python_exec, client_script, "--client-id", str(i)])
        client_processes.append(p)
        
    print("All clients started. Waiting for simulation to finish...")
    
    # Wait for server to finish
    server_process.wait()
    print("Server finished.")
    
    # Terminate clients if they haven't stopped
    for i, p in enumerate(client_processes, 1):
        if p.poll() is None:
            p.terminate()
            print(f"Terminated client {i}")
            
    print("Simulation complete.")

if __name__ == "__main__":
    main()
