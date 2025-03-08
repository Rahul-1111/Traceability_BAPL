"# Traceability_BAPL" 

---------------------------------------------------------------------------------------------------------------------------------------------------

pip install whitenoise
# Add it to MIDDLEWARE in settings.py
"whitenoise.middleware.WhiteNoiseMiddleware",  # Add this line
python manage.py collectstatic
daphne -p 8000 Traceability.asgi:application

---------------------------------------------------------------------------------------------------------------------------------------------------
# Step 1: Check the Current Remote URL
git remote -v

# Step 2: If the Remote is Wrong, Change It
git remote set-url origin https://github.com/Rahul-1111/Traceability_BAPL.git

git remote remove origin
git remote add origin https://github.com/Rahul-1111/Traceability_BAPL.git

# Step 3: Pull the Latest Changes from GitHub
git pull origin main --rebase

# Step 4: Push Your Changes Again
git push -u origin main --force 

# resolve issu
git push origin main
---------------------------------------------------------------------------------------------------------------------------------------------------