from datetime import date, timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from app.utils import salary_range_validator


class Job(models.Model):
    class JobStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        SCHEDULED = "SCHEDULED", "Scheduled"

    title = models.CharField("標題", max_length=255)
    desc = models.TextField("說明", blank=True)
    location = models.CharField("地點", max_length=255)
    salary_range = models.CharField(
        "薪資範圍", max_length=100, validators=[salary_range_validator], blank=True
    )  # Can change to JSONField if needed
    salary_range_avg = models.DecimalField(
        "薪資範圍平均",
        default=0,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(28590)],
    )
    company_name = models.CharField("公司名稱", max_length=255)
    posting_date = models.DateField("發布日期", default=date.today)
    expiration_date = models.DateField(
        "刊登期限", default=(timezone.now() + timedelta(days=14)).date()
    )
    required_skills = models.CharField(
        "必要技能", max_length=200, blank=True, help_text="逗號分隔的技能列表"
    )
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    status = models.CharField(
        max_length=10,
        choices=JobStatus.choices,
        default=JobStatus.ACTIVE,
    )

    def compute_salary_range_avg(self):
        if self.salary_range:
            parts = self.salary_range.split("~")
            if self.salary_range == "面議":
                return "40000"  # Return a default value for "面議"
            if len(parts) == 2:
                try:
                    min_salary = int(parts[0])
                    max_salary = int(parts[1])
                    return Decimal((min_salary + max_salary) // 2)
                except ValueError:
                    return None
        return None

    def save(self, *args, **kwargs):
        salary_range_avg = self.compute_salary_range_avg()
        self.salary_range_avg = salary_range_avg

        if self.expiration_date < date.today():
            self.status = "expired"
        elif self.posting_date > date.today():
            self.status = "scheduled"
        else:
            self.status = "active"
        super().save()

    class Meta:
        verbose_name = "工作職缺"
        verbose_name_plural = "工作職缺"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} at {self.company_name}"
