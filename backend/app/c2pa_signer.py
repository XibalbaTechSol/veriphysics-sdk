import os
from c2pa import Builder, Signer, C2paSigningAlg

class C2PASignerService:
    def __init__(self, cert_path: str, key_path: str):
        self.cert_path = cert_path
        self.key_path = key_path
        
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            raise FileNotFoundError(f"Certificate or Key file not found at {cert_path} or {key_path}")

        # Load signer
        try:
             # Read files as bytes
             with open(cert_path, "rb") as f:
                 cert_data = f.read()
             with open(key_path, "rb") as f:
                 key_data = f.read()

             self.signer = Signer(
                sign_cert=cert_data,
                private_key=key_data,
                alg=C2paSigningAlg.ES256, 
                tsa_url="http://timestamp.digicert.com"
            )
        except Exception as e:
            print(f"Error loading signer: {e}")
            raise e

    def sign_video(self, input_path: str, output_path: str, verification_data: dict) -> str:
        """
        Signs the video with C2PA manifest including physics verification assertion.
        Returns the path to the signed video.
        """
        
        # Define the manifest
        # We use a custom label for our physics assertion
        manifest = {
            "claim_generator": "VeriPhysics SDK/1.0",
            "assertions": [
                {
                    "label": "stds.veriphysics.assertion",
                    "data": verification_data
                }
            ]
        }
        
        try:
            builder = Builder(manifest)
            builder.sign_file(
                source_path=input_path,
                dest_path=output_path,
                signer=self.signer
            )
            return output_path
        except Exception as e:
            print(f"Error signing video: {e}")
            raise e
