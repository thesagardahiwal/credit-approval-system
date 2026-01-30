# Redis Caching Implementation

## Overview
Redis is now used for **credit score caching** to reduce database load on the `/check-eligibility` and `/create-loan` endpoints.

## What is Cached?

### Credit Score Calculation
- **Cache Key**: `credit_score:{customer_id}`
- **TTL**: 24 hours (86400 seconds)
- **Cache DB**: Redis DB 1 (separate from Celery broker DB 0)

## How It Works

### 1. **On Credit Score Calculation** (`calculate_credit_score`)
   - Check if score exists in Redis cache
   - If cached (within 24h) → Return immediately (no DB queries)
   - If not cached → Calculate from database aggregates
   - Store result in Redis with 24h TTL
   - Return score

### 2. **On New Loan Creation** (`create_loan`)
   - Create loan in database
   - **Automatically invalidate** the customer's credit score cache
   - Next eligibility check will recalculate fresh score

### 3. **Graceful Degradation**
   - All Redis operations wrapped in try-catch
   - If Redis is unavailable, calculations still work (no cache, but functional)

## Configuration

### Environment Variables
```
REDIS_HOST=redis          # Default: localhost
REDIS_PORT=6379          # Default: 6379
REDIS_DB=1               # Default: 1 (for caching, separate from Celery DB 0)
```

### Docker Compose
Updated `docker-compose.yml` with Redis configuration for both `web` and `worker` services.

## Performance Impact

### Before Caching
- Each eligibility check queries: Loans, EMIs, historical data
- Multiple DB queries per request
- High latency for repeated checks on same customer

### After Caching
- First check: Full calculation + Redis store (normal latency)
- Subsequent checks (within 24h): Redis lookup only (~1-5ms)
- **Expected improvement**: 80-90% faster for cached customers

## Implementation Files

| File | Changes |
|------|---------|
| `apps/loans/services/credit_score.py` | Added Redis import, cache lookup, cache storage, invalidation method |
| `apps/loans/services/loan_service.py` | Added `invalidate_cache()` call after loan creation |
| `apps/loans/tests.py` | Added `CreditScoreCachingTests` test class |
| `docker-compose.yml` | Added `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` env vars |

## Testing

Run cache-specific tests:
```bash
python manage.py test apps.loans.tests.CreditScoreCachingTests
```

### Test Cases
1. **test_credit_score_caching**: Verifies score is cached and retrieved
2. **test_cache_invalidation_on_new_loan**: Verifies cache clears after new loan

## Monitoring

### Check Cache Usage
```bash
# Connect to Redis
redis-cli -n 1

# View all cached scores
KEYS credit_score:*

# Get specific customer score
GET credit_score:1001

# Check TTL
TTL credit_score:1001
```

## Future Enhancements
- Add cache hit/miss metrics
- Implement cache warming for high-frequency customers
- Add Redis monitoring dashboard
- Consider caching monthly installment calculations as well
