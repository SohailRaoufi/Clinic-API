from rest_framework.decorators import APIView
from django.conf import settings
import os
import subprocess
import zipfile
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class BackupView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,_):
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            return Response({"detail": "Database file not found."}, status=status.HTTP_404_NOT_FOUND)

        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        dump_file_name = f"db_dump_{current_time}.sql"
        zip_file_name = f"db_dump_{current_time}.zip"

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        dump_file_path = os.path.join(desktop_path, dump_file_name)
        zip_file_path = os.path.join(desktop_path, zip_file_name)

        try:
            with open(dump_file_path, 'w') as dump_file:
                subprocess.run(['sqlite3', db_path, '.dump'], stdout=dump_file, check=True)

            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(dump_file_path, dump_file_name) 

            os.remove(dump_file_path)

            return Response({"detail": f"Database dump and zip successful. File saved to {zip_file_path}."}, status=status.HTTP_200_OK)

        except subprocess.CalledProcessError as e:
            return Response({"detail": f"Error during database dump: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"detail": f"Error during backup: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



