import boto3

s3 = boto3.client('s3')
bucket_name = 'my-finance-exports'

# ─── Define Lifecycle Configuration ─────────────────────────────
lifecycle_config = {
    'Rules': [{
        'ID': 'AutoExpirePortfolioExports',
        'Status': 'Enabled',
        'Filter': {'Prefix': 'portfolio_export/'},
        'Expiration': {'Days': 30},  # Auto-delete after 30 days
        'NoncurrentVersionExpiration': {'NoncurrentDays': 7}  # Old versions purged after 7 days
    }]
}

# ─── Apply Rules to Bucket ─────────────────────────────────────
s3.put_bucket_lifecycle_configuration(
    Bucket=bucket_name,
    LifecycleConfiguration=lifecycle_config
)

print(f"✅ Retention rules applied to bucket: {bucket_name}")
