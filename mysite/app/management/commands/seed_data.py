import random
import sys
import traceback
from datetime import timedelta

from app.models import Job
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

required_skills_candidates = [
    "Python",
    "Django",
    "JavaScript",
    "React",
    "Machine Learning",
    "Data Analysis",
    "Project Management",
    "UI/UX Design",
    "SEO",
    "Cloud Computing",
    "Agile Methodologies",
    "Communication Skills",
    "Problem Solving",
    "Team Collaboration",
    "Time Management",
    "Customer Service",
    "Renewable Energy Systems",
    "Medical Laboratory Techniques",
    "Logistics Management",
    "Supply Chain Optimization",
]

company_names = [
    "Tech Solutions Inc.",
    "Green Energy Co.",
    "HealthFirst Diagnostics",
    "Creative Designs Agency",
    "Global Logistics Ltd.",
    "Innovative Marketing Group",
    "Future Tech Innovations",
    "Smart Home Systems",
    "Urban Development Corp.",
    "Digital Media Hub",
    "Cloud Services Global",
    "E-commerce Ventures",
    "Cybersecurity Experts",
    "AI Research Labs",
    "Blockchain Solutions",
    "FinTech Innovations",
    "Healthcare Solutions",
    "Education Tech Partners",
    "Travel and Leisure Co.",
    "Food and Beverage Corp.",
]

job_titles = [
    "Software Engineer",
    "Senior Python Developer",
    "Frontend Developer (React)",
    "Data Scientist",
    "Product Manager",
    "UX/UI Designer",
    "Marketing Specialist",
    "Sales Executive",
    "Operations Manager",
    "Renewable Energy Technician",
    "Medical Lab Scientist",
    "Logistics Coordinator",
    "Supply Chain Analyst",
    "Project Coordinator",
    "Customer Support Specialist",
    "SEO Specialist",
    "Cloud Solutions Architect",
    "Agile Coach",
    "Cybersecurity Analyst",
    "AI Research Scientist",
    "Blockchain Developer",
    "Financial Analyst",
    "Healthcare Consultant",
    "Education Program Manager",
]


class Command(BaseCommand):
    help = "Seeds the database with initial test data for Jobs."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to seed database..."))

        try:
            with transaction.atomic():  # Use a transaction to ensure all or nothing
                # --- Create Jobs ---
                self.stdout.write(self.style.HTTP_INFO("Creating jobs..."))

                locations = [
                    "New York, NY",
                    "San Francisco, CA",
                    "Austin, TX",
                    "Remote",
                    "Berlin, Germany",
                    "London, UK",
                ]

                jobs_to_create = []
                num_jobs_per_company = 10  # Create a few jobs for each company

                current_time = timezone.now()

                for company in company_names:
                    for i in range(num_jobs_per_company):
                        title = random.choice(job_titles)
                        description = f"We are looking for a talented {title} to join our dynamic team at {company}. Responsibilities include..."
                        location = random.choice(locations)
                        if i == 0:
                            salary_range = "面議"
                            salary_range_avg = "40000"
                        else:
                            salary_upbound = str(random.randint(80000, 120000))
                            salary_lowbound = str(random.randint(30000, 80000))
                            salary_range = "~".join(
                                [
                                    salary_lowbound,
                                    salary_upbound,
                                ]
                            )
                            salary_range_avg = str(
                                (int(salary_lowbound) + int(salary_upbound)) // 2
                            )

                        posting_date = current_time - timedelta(
                            days=random.randint(60, 120)
                        )  # Posted in the past
                        expiration_date = posting_date + timedelta(
                            days=30 * 3
                        )  # Expires in 3 months

                        if expiration_date < current_time:
                            status = "expired"
                        elif posting_date > current_time:
                            status = "scheduled"
                        else:
                            status = "active"

                        required_skills = random.sample(
                            required_skills_candidates, k=random.randint(2, 6)
                        )  # Randomly select 1-5 skills

                        job_data = {
                            "title": f"{title} (Test Job #{i + 1})",
                            "desc": description,
                            "company_name": company,
                            "location": location,
                            "salary_range": salary_range,
                            "salary_range_avg": salary_range_avg,
                            "posting_date": posting_date,
                            "expiration_date": expiration_date,
                            "required_skills": ",".join(required_skills),
                            "status": status,
                        }
                        jobs_to_create.append(Job(**job_data))

                Job.objects.bulk_create(jobs_to_create)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {len(jobs_to_create)} jobs."
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS("Database seeding completed successfully!")
                )

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.stdout.write(
                self.style.ERROR(
                    f"An error occurred during seeding {exc_traceback}: {e}, traceback: {exc_type} - {exc_value}"
                )
            )
            # Alternatively, format the traceback into a string
            traceback_lines = traceback.format_exception(
                exc_type, exc_value, exc_traceback
            )
            print("Formatted Traceback:")
            print("".join(traceback_lines))
            # If in a transaction, it will be rolled back automatically on exception.
