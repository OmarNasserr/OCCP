from django.db import models

class Charger(models.Model):
    charge_point_id = models.CharField(max_length=100, unique=True)
    charge_point_model = models.CharField(max_length=100)
    charge_point_vendor = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="Connected")
    connected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.charge_point_id

class Transaction(models.Model):
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name="transactions")
    id_tag = models.CharField(max_length=100)
    connector_id = models.IntegerField()
    meter_start = models.IntegerField()
    meter_stop = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.id} for {self.charger.charge_point_id}"

class StatusLog(models.Model):
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name="status_logs")
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status log for {self.charger.charge_point_id} at {self.timestamp} - {self.status}"