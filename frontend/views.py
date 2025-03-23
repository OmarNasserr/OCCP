from django.shortcuts import render, get_object_or_404
from chargers.models import Charger
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import logging

logger = logging.getLogger(__name__)

running_simulators = {}

def dashboard(request):
    chargers = Charger.objects.all()
    return render(request, "frontend/dashboard.html", {"chargers": chargers})

def charger_detail(request, charge_point_id):
    charger = get_object_or_404(Charger, charge_point_id=charge_point_id)
    logs = charger.status_logs.all().order_by("-timestamp")
    return render(request, "frontend/charger_details.html", {"charger": charger, "logs": logs})


@csrf_exempt
def run_simulator(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        charger_id = data.get("charger_id")

        try:
            # Build the absolute path to simulator.py.
            simulator_path = os.path.join(settings.BASE_DIR, "simulator.py")
            process = subprocess.Popen(["python", simulator_path, charger_id])
            running_simulators[charger_id] = process  # Store the process in the dictionary
            return JsonResponse({"status": "success", "message": f"Simulator started for charger {charger_id}."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

@csrf_exempt
def stop_simulator(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        charger_id = data.get("charger_id")

        # Check if the simulator is running for the given charger_id
        if charger_id in running_simulators:
            process = running_simulators[charger_id]
            try:
                process.terminate()
                del running_simulators[charger_id]
                return JsonResponse({"status": "success", "message": f"Simulator stopped for charger {charger_id}."})
            except Exception as e:
                logger.error(f"Failed to stop simulator: {e}")
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
        else:
            return JsonResponse({"status": "error", "message": f"No running simulator found for charger {charger_id}."}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)
