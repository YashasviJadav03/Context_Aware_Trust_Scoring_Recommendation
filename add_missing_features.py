"""
Script to add missing features to notebook 7:
1. Feature Correlation Analysis
2. Cross-Validation
"""

print("=" * 80)
print("MISSING FEATURES IN NOTEBOOK 7")
print("=" * 80)

print("\n📋 SUMMARY OF WHAT'S MISSING:\n")

print("❌ 1. CROSS-VALIDATION")
print("   Current: Single train/val/test split (60/20/20)")
print("   Missing: K-Fold Cross-Validation for robust model evaluation")
print("   Where to add: After Section 5 (Train Models)")
print("   Add as: Section 5.5 - Cross-Validation Analysis")

print("\n❌ 2. FEATURE CORRELATION ANALYSIS")
print("   Current: No feature correlation analysis")
print("   Missing:")
print("      - Correlation with target variable")
print("      - Feature-to-feature correlation matrix")
print("      - Multicollinearity detection (VIF)")
print("   Where to add: After Section 3 (Feature Scaling)")
print("   Add as: Section 3.5 - Feature Correlation Analysis")

print("\n" + "=" * 80)
print("DETAILED IMPLEMENTATION GUIDE")
print("=" * 80)

print("\n" + "=" * 80)
print("SECTION 3.5: FEATURE CORRELATION ANALYSIS")
print("=" * 80)

print("""
### Cell 1: Correlation with Target Variable

```python
# Calculate correlation with target variable
target_corr = pd.DataFrame({
    'Feature': available_features,
    'Correlation': [X_train[col].corr(y_train) for col in available_features]
}).sort_values('Correlation', key=abs, ascending=False)

print("\\n" + "="*80)
print("FEATURE CORRELATION WITH TARGET (trust_score)")
print("="*80)
print(target_corr.to_string(index=False))
print("="*80)

# Identify highly correlated features
high_corr = target_corr[abs(target_corr['Correlation']) > 0.3]
print(f"\\n✅ Features with |correlation| > 0.3: {len(high_corr)}")
print(high_corr.to_string(index=False))

target_corr.to_csv('../results/reports/target_correlation.csv', index=False)
```

### Cell 2: Feature-to-Feature Correlation Matrix

```python
import seaborn as sns

# Calculate feature correlation matrix
corr_matrix = X_train.corr()

# Find highly correlated feature pairs
high_corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        if abs(corr_matrix.iloc[i, j]) > 0.7:
            high_corr_pairs.append({
                'Feature_1': corr_matrix.columns[i],
                'Feature_2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i, j]
            })

if high_corr_pairs:
    high_corr_df = pd.DataFrame(high_corr_pairs)
    print("\\nHighly Correlated Pairs:")
    print(high_corr_df.to_string(index=False))
else:
    print("\\n✅ No highly correlated pairs found")

# Visualize
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Feature Correlation Matrix')
plt.savefig('../results/figures/feature_correlation_matrix.png', dpi=300)
plt.show()
```

### Cell 3: Multicollinearity Detection (VIF)

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif_data = pd.DataFrame()
vif_data['Feature'] = available_features
vif_data['VIF'] = [variance_inflation_factor(X_train.values, i) 
                   for i in range(len(available_features))]
vif_data = vif_data.sort_values('VIF', ascending=False)

print("\\nVIF Analysis:")
print("VIF > 10: High multicollinearity")
print("VIF 5-10: Moderate multicollinearity")
print("VIF < 5: Low multicollinearity")
print(vif_data.to_string(index=False))

high_vif = vif_data[vif_data['VIF'] > 10]
if len(high_vif) > 0:
    print(f"\\n⚠️  {len(high_vif)} features with high VIF")
else:
    print("\\n✅ No high VIF features")

vif_data.to_csv('../results/reports/vif_analysis.csv', index=False)
```
""")

print("\n" + "=" * 80)
print("SECTION 5.5: CROSS-VALIDATION ANALYSIS")
print("=" * 80)

print("""
### Cell 1: K-Fold Cross-Validation

```python
from sklearn.model_selection import cross_val_score, KFold

# Setup K-Fold
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

print("\\n" + "="*80)
print("5-FOLD CROSS-VALIDATION RESULTS")
print("="*80)

cv_results = []

# Linear Regression
lr_cv_scores = cross_val_score(lr, X_train_scaled, y_train, 
                                cv=kfold, scoring='r2', n_jobs=-1)
lr_cv_spearman = cross_val_score(lr, X_train_scaled, y_train, 
                                  cv=kfold, 
                                  scoring=make_scorer(lambda y_true, y_pred: spearmanr(y_true, y_pred)[0]),
                                  n_jobs=-1)

cv_results.append({
    'Model': 'Linear Regression',
    'CV_R2_Mean': lr_cv_scores.mean(),
    'CV_R2_Std': lr_cv_scores.std(),
    'CV_Spearman_Mean': lr_cv_spearman.mean(),
    'CV_Spearman_Std': lr_cv_spearman.std()
})

print(f"Linear Regression:")
print(f"  R² CV: {lr_cv_scores.mean():.4f} (+/- {lr_cv_scores.std():.4f})")
print(f"  Spearman CV: {lr_cv_spearman.mean():.4f} (+/- {lr_cv_spearman.std():.4f})")

# Random Forest
rf_cv_scores = cross_val_score(rf, X_train, y_train, 
                                cv=kfold, scoring='r2', n_jobs=-1)
rf_cv_spearman = cross_val_score(rf, X_train, y_train, 
                                  cv=kfold,
                                  scoring=make_scorer(lambda y_true, y_pred: spearmanr(y_true, y_pred)[0]),
                                  n_jobs=-1)

cv_results.append({
    'Model': 'Random Forest',
    'CV_R2_Mean': rf_cv_scores.mean(),
    'CV_R2_Std': rf_cv_scores.std(),
    'CV_Spearman_Mean': rf_cv_spearman.mean(),
    'CV_Spearman_Std': rf_cv_spearman.std()
})

print(f"\\nRandom Forest:")
print(f"  R² CV: {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std():.4f})")
print(f"  Spearman CV: {rf_cv_spearman.mean():.4f} (+/- {rf_cv_spearman.std():.4f})")

# Gradient Boosting
gb_cv_scores = cross_val_score(gb, X_train, y_train, 
                                cv=kfold, scoring='r2', n_jobs=-1)
gb_cv_spearman = cross_val_score(gb, X_train, y_train, 
                                  cv=kfold,
                                  scoring=make_scorer(lambda y_true, y_pred: spearmanr(y_true, y_pred)[0]),
                                  n_jobs=-1)

cv_results.append({
    'Model': 'Gradient Boosting',
    'CV_R2_Mean': gb_cv_scores.mean(),
    'CV_R2_Std': gb_cv_scores.std(),
    'CV_Spearman_Mean': gb_cv_spearman.mean(),
    'CV_Spearman_Std': gb_cv_spearman.std()
})

print(f"\\nGradient Boosting:")
print(f"  R² CV: {gb_cv_scores.mean():.4f} (+/- {gb_cv_scores.std():.4f})")
print(f"  Spearman CV: {gb_cv_spearman.mean():.4f} (+/- {gb_cv_spearman.std():.4f})")

# XGBoost
xgb_cv_scores = cross_val_score(xgb, X_train, y_train, 
                                 cv=kfold, scoring='r2', n_jobs=-1)
xgb_cv_spearman = cross_val_score(xgb, X_train, y_train, 
                                   cv=kfold,
                                   scoring=make_scorer(lambda y_true, y_pred: spearmanr(y_true, y_pred)[0]),
                                   n_jobs=-1)

cv_results.append({
    'Model': 'XGBoost',
    'CV_R2_Mean': xgb_cv_scores.mean(),
    'CV_R2_Std': xgb_cv_scores.std(),
    'CV_Spearman_Mean': xgb_cv_spearman.mean(),
    'CV_Spearman_Std': xgb_cv_spearman.std()
})

print(f"\\nXGBoost:")
print(f"  R² CV: {xgb_cv_scores.mean():.4f} (+/- {xgb_cv_scores.std():.4f})")
print(f"  Spearman CV: {xgb_cv_spearman.mean():.4f} (+/- {xgb_cv_spearman.std():.4f})")

# Save CV results
cv_df = pd.DataFrame(cv_results)
cv_df.to_csv('../results/reports/cross_validation_results.csv', index=False)

print("\\n" + "="*80)
print("\\n✅ Cross-validation results saved")
```

### Cell 2: Cross-Validation Visualization

```python
# Visualize CV results
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

models = cv_df['Model']
x = np.arange(len(models))

# R² scores
axes[0].bar(x, cv_df['CV_R2_Mean'], yerr=cv_df['CV_R2_Std'], 
            capsize=5, color='skyblue', alpha=0.7)
axes[0].set_ylabel('R² Score')
axes[0].set_title('Cross-Validation R² Scores (5-Fold)', fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(models, rotation=15, ha='right')
axes[0].grid(axis='y', alpha=0.3)

# Spearman scores
axes[1].bar(x, cv_df['CV_Spearman_Mean'], yerr=cv_df['CV_Spearman_Std'], 
            capsize=5, color='lightcoral', alpha=0.7)
axes[1].set_ylabel('Spearman Correlation')
axes[1].set_title('Cross-Validation Spearman Scores (5-Fold)', fontweight='bold')
axes[1].set_xticks(x)
axes[1].set_xticklabels(models, rotation=15, ha='right')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../results/figures/cross_validation_results.png', dpi=300)
plt.show()

print("\\n✅ Visualization saved")
```
""")

print("\n" + "=" * 80)
print("BENEFITS OF THESE ADDITIONS")
print("=" * 80)

print("""
✅ FEATURE CORRELATION ANALYSIS:
   - Identifies which features are most predictive
   - Detects multicollinearity (redundant features)
   - Helps with feature selection
   - Improves model interpretability
   - Reduces overfitting by removing redundant features

✅ CROSS-VALIDATION:
   - More robust model evaluation
   - Reduces variance in performance estimates
   - Detects overfitting more reliably
   - Provides confidence intervals for metrics
   - Industry standard for model validation
""")

print("\n" + "=" * 80)
print("EXPECTED OUTPUT FILES")
print("=" * 80)

print("""
📁 results/reports/target_correlation.csv
📁 results/reports/vif_analysis.csv
📁 results/reports/cross_validation_results.csv

📁 results/figures/feature_correlation_matrix.png
📁 results/figures/cross_validation_results.png
""")

print("\n" + "=" * 80)
print("TO IMPLEMENT:")
print("=" * 80)
print("""
1. Open notebook 7 in Jupyter
2. Insert new cells after Section 3 (Feature Scaling)
3. Copy the code from "SECTION 3.5" above
4. Insert new cells after Section 5 (Train Models)
5. Copy the code from "SECTION 5.5" above
6. Run all cells
7. Check output files in results/
""")

print("\n✅ Implementation guide complete!")
