# Quick Start - 5 Minutes to Running

Get up and running in 5 minutes!

## Step 1: Setup (2 minutes)

**Choose your virtual environment:**

**Option A: venv (Standard Python)**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Linux/Mac
```

**Option B: Pipenv**
```bash
pip install pipenv
pipenv install
pipenv shell
```

## Step 2: Generate Data (30 seconds)

```bash
python sample_data.py
```

## Step 3: Test Conversion (1 minute)

```bash
python test_conversion.py
```

You should see:
- ✓ Claims loaded
- ✓ SQL query executed
- ✓ Python conversion executed
- ✓ Results compared
- ✓ Success message!

## Step 4: Run Pipeline (1 minute)

```bash
python run_pipeline.py
```

You should see:
- ✓ Database initialized
- ✓ Data loaded
- ✓ Aggregation completed
- ✓ Results saved
- ✓ Verification passed

## That's It! 🎉

You've successfully:
- ✅ Converted SQL to Python
- ✅ Run a complete pipeline
- ✅ Verified the results

**Next Steps:**
- Read `README.md` for more details
- Read `SETUP_GUIDE.md` for comprehensive setup
- Explore the code to understand how it works
- Try modifying the aggregation logic

