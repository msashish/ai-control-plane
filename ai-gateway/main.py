import os
import sys

if __name__ == "__main__":
    # 1. Map the directory scope pathing rules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    os.chdir(current_dir)

    # 2. LOCAL DEV BYPASS: Permit unset master key locally
    os.environ["LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY"] = "true"

    # 3. Laya callback is registered vua litellm_settings.callbacks

    # 4. Bind parameters seamlessly to the system arguments
    config_path = os.path.join(current_dir, "config.yaml")
    sys.argv = ["litellm", "--config", config_path, "--port", "4000"]

    # 6. Invoke the official CLI entry gateway bootstrap loop
    from litellm.proxy.proxy_cli import run_server
    
    print("Launching production LiteLLM gateway driven by config.yaml and laya_callback...")
    run_server()
