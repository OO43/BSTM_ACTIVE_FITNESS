from setuptools import setup, find_packages

setup(
    name="fastapi-fitness-centre",
    version="0.1.0",
    description="A FastAPI backend for a fitness centre management system.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "passlib[bcrypt]",
        "python-jose",
        "python-multipart",
        "pydantic"
    ],
    include_package_data=True,
    python_requires=">=3.8",
)