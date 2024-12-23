from datetime import datetime
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Basic,SelectedIposCollection
from django.http import JsonResponse
import random


class AddPanAPIView(APIView):
    def post(self, request):
        panNumber = request.data.get('panNumber')
        name = request.data.get('name')

        if not panNumber or not name:
            return Response({"error": "PAN number and name are required."}, status=status.HTTP_400_BAD_REQUEST)

        if Basic.find_one({"panNumber": panNumber}):
            return Response({"error": "PAN number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        newEntry = {"panNumber": panNumber, "name": name}
        result = Basic.insert_one(newEntry)

        newEntry["_id"] = str(result.inserted_id)

        return Response({"message": "PAN added successfully.", "data": newEntry}, status=status.HTTP_201_CREATED)

class GetAllPansAPIView(APIView):
    def get(self, request):
        pans = list(Basic.find({}, {"_id": 0}))  
        return Response(pans, status=status.HTTP_200_OK)
    
class GetIpoListAPIView(APIView):
    IPO_LIST = [
        "INTERNATIONAL GEMMOLOGICAL INSTITUTE INDIA LIMITED",
        "PURPLE UNITED SALES LIMITED",
        "SAI LIFE SCIENCE LIMITED",
        "VISHAL MEGA MART LIMITED",
        "NTPC GREEN ENERGY LIMITED",
        "DEEPAK BUILDERS & ENGINEERS INDIA LIMITED",
        "HYUNDAI MOTOR INDIA LIMITED",
    ]

    def get(self, request):
        return Response({"ipos": self.IPO_LIST}, status=status.HTTP_200_OK)


class SubmitIpoChoiceAPIView(APIView):
    def post(self, request):
        ipoChoice = request.data.get("ipoChoice")
        panNumber = request.data.get("panNumber")

        if ipoChoice not in GetIpoListAPIView.IPO_LIST:
            return Response(
                {"error": f"Invalid IPO choice. Available IPOs: {GetIpoListAPIView.IPO_LIST}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not panNumber:
            return Response({"error": "PAN number is required."}, status=status.HTTP_400_BAD_REQUEST)

        panExists = Basic.find_one({"panNumber": panNumber})
        if not panExists:
            return Response({"error": "PAN number does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        ipo_data = {
            "ipoChoice": ipoChoice,
            "panNumber": panNumber,
            "timestamp": datetime.utcnow().isoformat(),  # Convert datetime to ISO 8601 string
        }
        
        SelectedIposCollection.insert_one(ipo_data)

        return Response(
            {"message": f"Your choice '{ipoChoice}' has been submitted successfully."},
            status=status.HTTP_201_CREATED,
        )
    
class FetchPanNumbersAPIView(APIView):
    def post(self, request):
        ipoName = request.data.get("ipoName")
        
        if not ipoName:
            return Response(
                {"error": "IPO name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            panNumbers = list(
                SelectedIposCollection.find({"ipoChoice": ipoName}, {"_id": 0, "panNumber": 1})
            )
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not panNumbers:
            return Response(
                {"message": f"No PAN numbers found for the IPO '{ipoName}'."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Return the list of PAN numbers
        return JsonResponse(
            {"ipoName": ipoName, "panNumbers": [p["panNumber"] for p in panNumbers]},
            status=status.HTTP_200_OK,
        )

class IpoStatusAPIView(APIView):
    def post(self, request):
        ipoName = request.data.get("ipoName")

        if not ipoName:
            return Response(
                {"error": "IPO name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            panNumbers = list(
                SelectedIposCollection.find({"ipoChoice": ipoName}, {"_id": 0, "panNumber": 1})
            )
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not panNumbers:
            return Response(
                {"message": f"No PAN numbers found for the IPO '{ipoName}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        updated_status = []
        for pan in panNumbers:
            panNumber = pan["panNumber"]
            try:
                statusOptions = ["Success", "Failed", "Pending"]
                ipoStatus = random.choice(statusOptions)

                SelectedIposCollection.update_one(
                    {"panNumber": panNumber, "ipoChoice": ipoName},
                    {"$set": {"ipoStatus": ipoStatus}}
                )

                updated_status.append({"panNumber": panNumber, "ipoStatus": ipoStatus})
            except Exception:
                SelectedIposCollection.update_one(
                    {"panNumber": panNumber, "ipoChoice": ipoName},
                    {"$set": {"ipoStatus": "Invalid"}}
                )
                updated_status.append({"panNumber": panNumber, "ipoStatus": "Invalid"})

        return JsonResponse(
            {"ipoName": ipoName, "updatedStatus": updated_status},
            status=status.HTTP_200_OK,
        )