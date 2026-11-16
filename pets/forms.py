from django import forms

from pets.models import Pet


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name",
            "species",
            "owner",
            "weight_kg",
            "recommended_weight_kg",
        ]
        labels = {
            "name": "Имя питомца",
            "species": "Вид",
            "owner": "Хозяин",
            "weight_kg": "Текущий вес, кг",
            "recommended_weight_kg": "Рекомендуемый вес, кг",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "species": forms.TextInput(attrs={"class": "form-control"}),
            "owner": forms.Select(attrs={"class": "form-select"}),
            "weight_kg": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "recommended_weight_kg": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Имя питомца обязательно.")
        return name

    def clean_weight_kg(self):
        value = self.cleaned_data.get("weight_kg")
        if value is not None and value < 0:
            raise forms.ValidationError("Вес не может быть отрицательным.")
        return value

    def clean_recommended_weight_kg(self):
        value = self.cleaned_data.get("recommended_weight_kg")
        if value is not None and value <= 0:
            raise forms.ValidationError("Рекомендуемый вес должен быть больше нуля.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get("weight_kg")
        recommended = cleaned_data.get("recommended_weight_kg")
        if weight is not None and recommended is not None and weight > recommended * 1.5:
            raise forms.ValidationError(
                "Текущий вес превышает рекомендуемый более чем в 1,5 раза. "
                "Проверьте, что данные введены корректно."
            )
        return cleaned_data
