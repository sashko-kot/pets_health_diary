from django import forms
from django.utils import timezone

from records.models import HealthRecord


class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = [
            "pet",
            "recorded_on",
            "activity",
            "appetite",
            "symptoms",
            "weight_kg",
        ]
        labels = {
            "pet": "Питомец",
            "recorded_on": "Дата осмотра",
            "activity": "Активность",
            "appetite": "Аппетит",
            "symptoms": "Симптомы",
            "weight_kg": "Вес на осмотре, кг",
        }
        widgets = {
            "pet": forms.Select(attrs={"class": "form-select"}),
            "recorded_on": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "activity": forms.TextInput(attrs={"class": "form-control"}),
            "appetite": forms.TextInput(attrs={"class": "form-control"}),
            "symptoms": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "weight_kg": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
        }

    def clean_recorded_on(self):
        recorded_on = self.cleaned_data.get("recorded_on")
        if recorded_on is None:
            raise forms.ValidationError("Укажите дату осмотра.")
        if recorded_on > timezone.localdate():
            raise forms.ValidationError("Дата осмотра не может быть в будущем.")
        return recorded_on

    def clean_activity(self):
        value = (self.cleaned_data.get("activity") or "").strip()
        if not value:
            raise forms.ValidationError("Укажите активность питомца.")
        return value

    def clean_appetite(self):
        value = (self.cleaned_data.get("appetite") or "").strip()
        if not value:
            raise forms.ValidationError("Укажите состояние аппетита.")
        return value

    def clean_weight_kg(self):
        value = self.cleaned_data.get("weight_kg")
        if value is not None and value < 0:
            raise forms.ValidationError("Вес не может быть отрицательным.")
        return value
