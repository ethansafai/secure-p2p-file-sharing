from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dsa
from cryptography.hazmat.primitives.asymmetric.types\
  import CertificatePublicKeyTypes
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_certificate_public_key(cert_file_path: str)\
  -> CertificatePublicKeyTypes:
  """Extract the public key from a public key certificate"""
  with open(cert_file_path, 'rb') as cert_file:
      cert_data = cert_file.read()
  certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
  public_key = certificate.public_key()
  return public_key

def verify_digital_signature(file_data: str,
                             public_key: rsa.RSAPublicKey | dsa.DSAPublicKey,
                             received_signature: bytes) -> bool:
  """Verify the digital signature of file data"""
  try:
    file_bytes = file_data.encode()
    # check the key type (RSA or DSA)
    if isinstance(public_key, rsa.RSAPublicKey):
      public_key.verify(received_signature, file_bytes,
                        padding.PKCS1v15(), hashes.SHA256())
      return True
    elif isinstance(public_key, dsa.DSAPublicKey):
      public_key.verify(received_signature, file_bytes, hashes.SHA256())
      return True
    else:
      raise Exception(f'Unsupported public key type: {type(public_key)}')
  except InvalidSignature:
    return False

def signature_is_valid(cert_file_path: str, file_data: str,
                       received_signature: bytes) -> bool:
  """Check if the received digital signature is valid using the sender's public
  key"""
  public_key = load_certificate_public_key(cert_file_path)
  return verify_digital_signature(file_data, public_key, received_signature)

def load_private_key(key_file_path: str):
  """Load a private key from a key file"""
  with open(key_file_path, 'rb') as key_file:
    private_key_data = key_file.read()
  private_key = serialization.load_pem_private_key(private_key_data, 
                                                   password=None,
                                                   backend=default_backend())
  return private_key

def generate_signature(key_file_path: str, file_data: str) -> bytes:
  """Generate a digital signature of a file using the sender's private key"""
  private_key = load_private_key(key_file_path)
  file_bytes = file_data.encode()
  # check the key type (RSA or DSA)
  if isinstance(private_key, rsa.RSAPrivateKey):
    return private_key.sign(file_bytes, padding.PKCS1v15(), hashes.SHA256())
  elif isinstance(private_key, dsa.DSAPrivateKey):
    return private_key.sign(file_bytes, hashes.SHA256())
  else:
    raise Exception(f'Unsupported private key type: {type(private_key)}')
