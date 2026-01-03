
import subprocess
import os
import json
import logging

logger = logging.getLogger(__name__)

class MotionVerifierWrapper:
    def __init__(self, cli_path: str):
        self.cli_path = cli_path
        if not os.path.exists(cli_path):
            raise FileNotFoundError(f"Verifier CLI not found at: {cli_path}")

    def verify(self, video_path: str, gyro_path: str) -> dict:
        """
        Runs the C++ verifier CLI on the given files.
        Returns a dict with keys: verified (bool), score (float), message (str), details (dict)
        """
        if not os.path.exists(video_path):
            return {"verified": False, "score": 0.0, "message": f"Video not found: {video_path}"}
        if not os.path.exists(gyro_path):
            return {"verified": False, "score": 0.0, "message": f"Gyro CSV not found: {gyro_path}"}

        try:
            # Run the CLI
            result = subprocess.run(
                [self.cli_path, video_path, gyro_path],
                capture_output=True,
                text=True,
                check=False # We handle return codes manually
            )

            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode

            # Parse Output (Parsing the stdout format from main.cpp)
            # SUCCESS: Analysis complete. ...
            # SCORE: 0.98...
            # VERDICT: REAL...
            
            score = 0.0
            is_consistent = False
            message = "Verification failed"
            response_details = {} # Store new metrics here

            for line in stdout.splitlines():
                if line.startswith("SCORE:"):
                    try:
                        score = float(line.split(":")[1].strip())
                    except ValueError:
                        pass
                if line.startswith("VERDICT:"):
                    verdict = line.split(":")[1].strip()
                    if "REAL" in verdict or "CONSISTENT" in verdict:
                        is_consistent = True
                    message = verdict
                if line.startswith("SUCCESS:") and not message:
                     message = line.split(":")[1].strip()
                
                # New metrics
                if line.startswith("CAUSALITY_SCORE:"):
                    try:
                        response_details["causality_score"] = float(line.split(":")[1].strip())
                    except ValueError: pass
                if line.startswith("IS_HANDHELD:"):
                    val = line.split(":")[1].strip().lower()
                    response_details["is_handheld"] = (val == "true")
                if line.startswith("TREMOR_ENERGY:"):
                    try:
                        response_details["tremor_energy"] = float(line.split(":")[1].strip())
                    except ValueError: pass

            response = {
                "verified": is_consistent,
                "score": score,
                "message": message,
                "details": response_details, # Pass these up
                "raw_output": stdout,
                "error_output": stderr
            }
            
            if return_code != 0:
                 response["verified"] = False
                 response["message"] = f"CLI Error (Code {return_code})"

            return response

        except Exception as e:
            logger.exception("Error running verification CLI")
            return {
                "verified": False,
                "score": 0.0,
                "message": str(e)
            }
