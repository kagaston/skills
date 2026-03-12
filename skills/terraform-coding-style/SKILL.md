---
name: terraform-coding-style
description: Terraform coding standards including plan-first workflow, quality gates, naming conventions, debugging, and YAML-driven patterns. Use when writing or reviewing Terraform code or managing infrastructure changes.
---

# Terraform Coding Style

## Plan-First Workflow (The Golden Rule)

EVERY Terraform change MUST follow plan-first. No exceptions.

1. Run `terraform plan` (or `just plan-dev`) before any change
2. Review plan output for unexpected changes
3. Make code changes
4. Run `terraform validate` for syntax
5. Run `terraform plan` again to verify
6. Run quality gate
7. Commit only when plan matches expectations

**Re-plan triggers:** any code change, validation fixes, linter fixes, state operations, provider upgrades, variable changes

## Quality Gate

Run all checks before committing:

```bash
terraform fmt -recursive -check    # Formatting
tflint --recursive                 # Linting
terraform validate                 # Syntax validation
terraform plan                     # Verify changes
```

**justfile:**

```just
fmt:
    terraform fmt -recursive

lint:
    tflint --recursive

validate:
    terraform init -backend=false
    terraform validate

quality: fmt lint validate
    just plan-dev
```

## Naming Conventions

- **Resources:** `snake_case` (`aws_iam_role.lambda_execution`)
- **Files:** `snake_case.tf` organized by resource type (`teams.tf`, `services.tf`)
- **Variables:** `snake_case` with descriptions
- **No hardcoded IDs** — use variables, data sources, or config files

## File Organization

- Flat structure by resource type: `providers.tf`, `variables.tf`, `outputs.tf`, `data.tf`, `{resource_type}.tf`
- Keep files under 300 lines
- One type of resource per file

## YAML-Driven Configuration Pattern

Store resource configs in YAML files, load with `yamldecode()` + `fileset()`:

```hcl
locals {
  config_files = fileset("${path.root}/configs", "**/*.yaml")
  configs = {
    for f in local.config_files :
    f => yamldecode(file("${path.root}/configs/${f}"))
  }
}
```

Use `for_each` with decoded YAML maps for resource creation.

## Environment Separation

- Same code across all environments (DRY)
- Different variables per environment in `tfvars/`
- Separate state files per workspace

## Debugging & Fixing

**Root cause analysis:** What failed? What changed? Expected vs actual? Blast radius?

**Common issues:**

| Issue | Likely cause |
|-------|--------------|
| Unexpected plan changes | State drift (manual changes), check with `terraform show` |
| Validation errors | Syntax errors, missing attributes, type mismatches |
| Apply failures | API errors, resource conflicts, permission issues |
| State lock errors | Previous run interrupted, use `terraform force-unlock <id>` after confirming no active runs |

**Emergency procedure for unexpected plan output:**

1. **STOP** — do not apply
2. **Investigate** — why is plan different?
3. **Root cause** — state drift? code error? provider issue?
4. **Fix and re-plan**
5. **Document** if pattern emerges

## Anti-Patterns

- Don't use `count` when `for_each` is more appropriate
- Don't hardcode IDs
- Don't create nested module structures (keep flat)
- Don't skip validation before planning
- Don't commit without running quality gate

## Verification Checklist

- [ ] Plan-first workflow followed
- [ ] `terraform fmt` passes
- [ ] `tflint` passes
- [ ] `terraform validate` passes
- [ ] Plan shows expected changes only
- [ ] All variables have descriptions
- [ ] No hardcoded IDs or secrets
- [ ] snake_case naming throughout
