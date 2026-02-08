# Usage Examples

This page provides practical examples of using plaintest in different scenarios.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Customizing Test Case Templates](#customizing-test-case-templates)
- [Working with Multiple Test Cases](#working-with-multiple-test-cases)
- [Using Tags to Organize Tests](#using-tags-to-organize-tests)
- [Linking Multiple Tests to One Case](#linking-multiple-tests-to-one-case)
- [Adding Images and Media](#adding-images-and-media)
- [Integration with CI/CD](#integration-with-cicd)
- [Working with Test Classes](#working-with-test-classes)
- [Advanced Markdown Features](#advanced-markdown-features)

## Basic Usage

### Creating Test Cases Interactively

The `add` command supports interactive creation of multiple test cases:

```bash
plaintest add
```

You'll be prompted for each test case title:

```
Enter test case title: User registration with valid data
✓ Created test-cases/001/case.md
Add another test case? [Y/n]: y
Enter test case title: User registration with invalid email
✓ Created test-cases/002/case.md
Add another test case? [Y/n]: n
Done!
```

### Creating a Single Test Case

Provide the title as an argument to skip the interactive prompts:

```bash
plaintest add "Password reset flow"
```

## Working with Multiple Test Cases

### Creating a Test Suite

Let's create a complete authentication test suite:

```bash
plaintest add "User login with valid credentials"
plaintest add "User login with invalid password"
plaintest add "User login with non-existent email"
plaintest add "User logout"
plaintest add "Session persistence"
```

This creates test cases 001-005 in separate directories.

### Linking Tests to Cases

```python
# tests/test_authentication.py
import pytest
from plaintest.markers import tc
from myapp import auth

@tc("001")
def test_login_valid_credentials():
    """User can login with valid credentials"""
    result = auth.login("user@example.com", "ValidPass123")
    assert result.success is True
    assert result.user.email == "user@example.com"

@tc("002")
def test_login_invalid_password():
    """Login fails with invalid password"""
    result = auth.login("user@example.com", "WrongPassword")
    assert result.success is False
    assert "Invalid password" in result.error

@tc("003")
def test_login_nonexistent_email():
    """Login fails with non-existent email"""
    result = auth.login("nobody@example.com", "AnyPassword")
    assert result.success is False
    assert "User not found" in result.error

@tc("004")
def test_logout():
    """User can logout successfully"""
    auth.login("user@example.com", "ValidPass123")
    result = auth.logout()
    assert result.success is True
    assert auth.current_user() is None

@tc("005")
def test_session_persistence():
    """Session persists across requests"""
    session_id = auth.login("user@example.com", "ValidPass123").session_id
    user = auth.get_user_by_session(session_id)
    assert user is not None
    assert user.email == "user@example.com"
```

## Using Tags to Organize Tests

Tags help categorize and filter test cases. Add them in the frontmatter:

```markdown
---
title: User login with valid credentials
tags: [authentication, smoke, critical, regression]
---

## Steps
1. Navigate to /login
2. Enter email: user@example.com
3. Enter password: ValidPass123
4. Click "Login" button

## Expected
- Redirect to /dashboard
- Display welcome message
- Create session cookie
```

### Common Tagging Patterns

**By Test Type:**
```yaml
tags: [smoke, regression, integration, e2e, unit]
```

**By Priority:**
```yaml
tags: [critical, high, medium, low]
```

**By Feature Area:**
```yaml
tags: [authentication, payments, search, checkout]
```

**By Platform:**
```yaml
tags: [web, mobile, api, desktop]
```

**Combined:**
```yaml
tags: [authentication, critical, smoke, web, regression]
```

## Linking Multiple Tests to One Case

One test case can have multiple test implementations (e.g., for different browsers or environments):

```python
# tests/test_login_browsers.py
import pytest
from plaintest.markers import tc

@tc("001")
def test_login_chrome():
    """Test login in Chrome browser"""
    driver = setup_chrome()
    perform_login(driver)
    assert is_logged_in(driver)

@tc("001")
def test_login_firefox():
    """Test login in Firefox browser"""
    driver = setup_firefox()
    perform_login(driver)
    assert is_logged_in(driver)

@tc("001")
def test_login_safari():
    """Test login in Safari browser"""
    driver = setup_safari()
    perform_login(driver)
    assert is_logged_in(driver)
```

All three tests will be linked to test case 001 in the HTML report.

## Adding Images and Media

Include screenshots, diagrams, and other media in your test cases:

### Adding Images

1. Place the image in the test case directory:
```
test-cases/
└── 001/
    ├── case.md
    ├── login-form.png
    └── success-dashboard.png
```

2. Reference it in your Markdown:
```markdown
---
title: User login flow
tags: [authentication]
---

## Steps

1. Navigate to the login form

![Login Form](login-form.png)

2. Enter credentials and submit

## Expected

User sees the dashboard:

![Success Dashboard](success-dashboard.png)
```

### Supported Media Types

- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`
- Videos: `.mp4`, `.webm` (use HTML5 video tags)
- Other files: Can be linked but won't be embedded

### Example with Multiple Images

```markdown
---
title: E-commerce checkout flow
tags: [checkout, e2e, critical]
---

## Steps

1. Add items to cart
   ![Cart with items](step1-cart.png)

2. Proceed to checkout
   ![Checkout page](step2-checkout.png)

3. Enter shipping information
   ![Shipping form](step3-shipping.png)

4. Enter payment details
   ![Payment form](step4-payment.png)

5. Confirm order
   ![Order confirmation](step5-confirm.png)

## Expected

- Order is placed successfully
- Confirmation email is sent
- Order appears in user's account
```

## Integration with CI/CD

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest
      
      - name: Run tests
        run: pytest
      
      - name: Check test case coverage
        run: plaintest report
      
      - name: Generate HTML report
        if: always()
        run: plaintest html-report
      
      - name: Upload HTML report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: .plaintest/plaintest-report.html
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  image: python:3.13
  script:
    - pip install -e .
    - pip install pytest
    - pytest
    - plaintest report
    - plaintest html-report
  artifacts:
    when: always
    paths:
      - .plaintest/plaintest-report.html
    expire_in: 1 week
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -e .'
                sh 'pip install pytest'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest'
            }
        }
        
        stage('Coverage Report') {
            steps {
                sh 'plaintest report || true'
            }
        }
        
        stage('HTML Report') {
            steps {
                sh 'plaintest html-report'
                publishHTML([
                    reportDir: '.plaintest',
                    reportFiles: 'plaintest-report.html',
                    reportName: 'Test Case Report'
                ])
            }
        }
    }
}
```

### Failing the Build on Low Coverage

The `plaintest report` command exits with the number of uncovered test cases, which can be used to fail CI builds:

```bash
# In your CI script
plaintest report
# Build will fail if there are any uncovered test cases
```

To allow some uncovered cases, check the exit code:

```bash
plaintest report
coverage_exit_code=$?
if [ $coverage_exit_code -gt 5 ]; then
    echo "Too many uncovered test cases: $coverage_exit_code"
    exit 1
fi
```

## Working with Test Classes

plaintest works with pytest test classes:

```python
# tests/test_user_management.py
import pytest
from plaintest.markers import tc

class TestUserRegistration:
    
    @tc("010")
    def test_register_valid_data(self):
        """User can register with valid data"""
        user = register_user(
            email="new@example.com",
            password="SecurePass123"
        )
        assert user.id is not None
        assert user.email == "new@example.com"
    
    @tc("011")
    def test_register_duplicate_email(self):
        """Cannot register with existing email"""
        register_user("existing@example.com", "Pass123")
        with pytest.raises(DuplicateEmailError):
            register_user("existing@example.com", "Pass456")
    
    @tc("012")
    def test_register_weak_password(self):
        """Cannot register with weak password"""
        with pytest.raises(WeakPasswordError):
            register_user("user@example.com", "123")

class TestUserProfile:
    
    @tc("020")
    def test_update_profile(self):
        """User can update profile information"""
        user = get_user("user@example.com")
        user.update_profile(name="John Doe", bio="Developer")
        assert user.name == "John Doe"
        assert user.bio == "Developer"
    
    @tc("021")
    def test_upload_avatar(self):
        """User can upload avatar image"""
        user = get_user("user@example.com")
        user.upload_avatar("avatar.jpg")
        assert user.avatar_url.endswith("avatar.jpg")
```

## Advanced Markdown Features

### Using Code Blocks in Test Cases

```markdown
---
title: API authentication test
tags: [api, authentication]
---

## Steps

1. Make a request to the login endpoint:

```bash
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

2. Extract the token from the response

## Expected

Response contains a valid JWT token:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 123,
    "email": "user@example.com"
  }
}
```
```

### Using Tables

```markdown
---
title: Input validation tests
tags: [validation]
---

## Test Data

| Input | Expected Result |
|-------|----------------|
| valid@email.com | ✓ Valid |
| invalid-email | ✗ Invalid |
| @example.com | ✗ Invalid |
| user@.com | ✗ Invalid |
| user@example | ✗ Invalid |

## Steps

1. Test each input from the table above
2. Verify the validation result matches expected

## Expected

All validation results match the expected column
```

### Using Lists and Checklists

```markdown
---
title: Pre-deployment checklist
tags: [deployment, checklist]
---

## Prerequisites

Before deploying, ensure:

- [ ] All tests pass
- [ ] Code review approved
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Backup created
- [ ] Rollback plan documented

## Steps

1. Run final test suite
2. Deploy to staging
3. Verify staging environment
4. Deploy to production
5. Monitor logs for 15 minutes

## Expected

- Deployment completes without errors
- All services are healthy
- No error spikes in monitoring
```

### Using Quotes and Notes

```markdown
---
title: Payment processing
tags: [payments, critical]
---

## Important Notes

> **Security Note:** This test uses test credit card numbers from the payment gateway's documentation. Never use real credit card numbers in tests.

> **Environment:** This test requires the sandbox payment gateway to be configured.

## Steps

1. Add items to cart (total: $49.99)
2. Proceed to checkout
3. Enter test credit card:
   - Number: 4242 4242 4242 4242
   - Expiry: 12/25
   - CVV: 123
4. Submit payment

## Expected

- Payment is processed successfully
- Order status changes to "Paid"
- Confirmation email is sent
```

## Tips and Best Practices

### 1. Keep Test Cases Focused

Each test case should verify one specific behavior:

✅ Good:
```
001 - User login with valid credentials
002 - User login with invalid password
003 - User login with non-existent email
```

❌ Too broad:
```
001 - Complete user authentication system
```

### 2. Use Descriptive Titles

✅ Good:
```
"User can filter products by price range"
```

❌ Too vague:
```
"Product test"
```

### 3. Document Prerequisites

```markdown
---
title: Export report to PDF
tags: [reports, export]
---

## Prerequisites

- User must be logged in
- At least one report must exist
- User must have "export" permission

## Steps
...
```

### 4. Include Expected Errors

```markdown
---
title: Invalid payment processing
tags: [payments, negative-test]
---

## Steps

1. Submit payment with expired card

## Expected

- Payment is rejected
- Error message: "Card has expired"
- Order status remains "Pending"
- User is prompted to use different card
```

### 5. Version Control Your Test Cases

Commit test cases along with the code they test:

```bash
git add test-cases/042/case.md tests/test_new_feature.py
git commit -m "Add test case for new feature"
```

This ensures test documentation stays in sync with the codebase!

