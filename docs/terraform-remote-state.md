# Terraform remote state

Terraform state can contain infrastructure identifiers and sensitive values even
when the Terraform source contains no credentials. This project must use an
access-controlled remote backend before another apply.

## Target design

- Store state in a dedicated private S3 bucket that is managed separately from
  this application's state.
- Enable S3 Versioning so accidental overwrites and deletions can be recovered.
- Keep all four S3 Block Public Access settings enabled.
- Enable default server-side encryption. SSE-S3 is a reasonable baseline for
  this portfolio project; use a customer-managed KMS key when separate key
  policy control and auditability justify the additional cost and IAM work.
- Require TLS in the bucket policy.
- Use Terraform's S3 lock file with `use_lockfile = true`. DynamoDB-based
  locking is deprecated in current Terraform.
- Restrict the Terraform operator role to the selected state key and its
  `.tflock` object. The state object requires GetObject and PutObject. The lock
  object also requires DeleteObject. Restrict ListBucket to the selected prefix.
- Supply AWS credentials through the normal AWS profile or workload identity.
  Never put access keys, secret keys, session tokens, or passwords in backend
  configuration.

The committed `backend.tf` contains only fixed security behavior. Copy
`backend.hcl.example` to ignored `backend.hcl` and provide the deployment
specific bucket, key, region, and optional KMS key there.

## Migration gate

Do not migrate from a public state file or assume that the state in Git history
is authoritative. The locally modified state must remain untouched until its
ownership and purpose are reviewed.

After the backend has been provisioned separately and an operator has explicitly
approved AWS access:

1. Confirm the AWS profile, Region, and account with `aws sts get-caller-identity`.
2. Preserve the authoritative local state in an encrypted, access-restricted
   backup outside the repository.
3. Review `backend.hcl` and its target bucket and object key.
4. Run `terraform init -migrate-state -backend-config=backend.hcl`.
5. Review Terraform's migration prompt before accepting it.
6. Verify state listing and backend object versioning without printing state.
7. Run a refresh-only plan and review it before any ordinary plan or apply.

Avoid manual `terraform state push`. It can overwrite remote state and should
be reserved for a separately reviewed recovery procedure.

References:

- https://developer.hashicorp.com/terraform/language/backend/s3
- https://developer.hashicorp.com/terraform/language/state/backends
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
