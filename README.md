"# Traceability_BAPL" 

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