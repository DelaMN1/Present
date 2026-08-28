from django import forms

from courses.models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("code", "name", "academic_period", "description")
        widgets = {
            "code": forms.TextInput(
                attrs={"class": "input", "placeholder": "BIOC 301", "autocomplete": "off"}
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Clinical Biochemistry",
                    "autocomplete": "off",
                }
            ),
            "academic_period": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "2026/2027 First Semester",
                    "autocomplete": "off",
                }
            ),
            "description": forms.Textarea(attrs={"class": "input", "rows": 4}),
        }

    def clean_code(self):
        return (self.cleaned_data.get("code") or "").strip()

    def clean_name(self):
        return (self.cleaned_data.get("name") or "").strip()

    def clean_academic_period(self):
        return (self.cleaned_data.get("academic_period") or "").strip()

    def clean(self):
        cleaned = super().clean()
        lecturer = getattr(self.instance, "lecturer", None)
        code = cleaned.get("code")
        period = cleaned.get("academic_period")
        if lecturer and code and period:
            clash = Course.objects.filter(
                lecturer=lecturer,
                code__iexact=code,
                academic_period__iexact=period,
            )
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise forms.ValidationError(
                    "You already have a course with this code in that academic period."
                )
        return cleaned


class CourseDeleteForm(forms.Form):
    confirmation = forms.CharField(
        label="Type the course code to confirm",
        widget=forms.TextInput(attrs={"class": "input", "autocomplete": "off"}),
    )

    def __init__(self, *args, course, **kwargs):
        self.course = course
        super().__init__(*args, **kwargs)

    def clean_confirmation(self):
        value = (self.cleaned_data.get("confirmation") or "").strip()
        if value != self.course.code:
            raise forms.ValidationError("That does not match the course code.")
        return value
