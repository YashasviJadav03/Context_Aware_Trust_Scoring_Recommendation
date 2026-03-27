# CSV Loading Troubleshooting Guide

## Problem: ParserError when loading trust_scored_dataset.csv

### Quick Fixes

#### 1. **Use Python Engine** (Most Common Fix)
```python
df = pd.read_csv("../data/processed/trust_scored_dataset.csv", engine='python')
```

#### 2. **Skip Bad Lines**
```python
df = pd.read_csv("../data/processed/trust_scored_dataset.csv", 
                engine='python', 
                on_bad_lines='skip')
```

#### 3. **Handle Large Files**
```python
df = pd.read_csv("../data/processed/trust_scored_dataset.csv", 
                engine='python', 
                on_bad_lines='skip',
                low_memory=False)
```

#### 4. **Load in Chunks** (For Very Large Files)
```python
chunk_list = []
for chunk in pd.read_csv("../data/processed/trust_scored_dataset.csv", 
                        chunksize=50000, 
                        engine='python'):
    chunk_list.append(chunk)
    if len(chunk_list) >= 10:  # Limit to 500k rows
        break

df = pd.concat(chunk_list, ignore_index=True)
```

### Why This Happens

1. **File Size**: Your CSV is ~305MB (719,967 rows), which can cause memory issues
2. **Encoding Issues**: Mixed character encodings in the data
3. **Malformed Lines**: Some rows might have inconsistent formatting
4. **Memory Constraints**: Default C parser runs out of memory

### Current Status

✅ **File exists**: `data/processed/trust_scored_dataset.csv` (305MB)
✅ **File is readable**: Standard pandas can load it
✅ **Data is valid**: 719,967 rows × 29 columns
✅ **Trust scores present**: Range 0.000 - 0.998

### Updated Notebook

The notebook has been updated to use:
```python
df = pd.read_csv("../data/processed/trust_scored_dataset.csv", 
                engine='python', 
                on_bad_lines='skip')
```

This should resolve the ParserError.

### If Problems Persist

1. **Check available memory**: 
   ```python
   import psutil
   print(f"Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB")
   ```

2. **Use sample data**:
   ```python
   # Load first 100k rows only
   df = pd.read_csv("../data/processed/trust_scored_dataset.csv", 
                   nrows=100000, 
                   engine='python')
   ```

3. **Check file integrity**:
   ```bash
   head -5 data/processed/trust_scored_dataset.csv
   tail -5 data/processed/trust_scored_dataset.csv
   ```

### Alternative: Use Sample Dataset

If issues persist, run:
```bash
python fix_csv.py
```

This creates a sample dataset (`trust_scored_dataset_sample.csv`) with the same structure for testing.