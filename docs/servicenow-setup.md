# 🔧 ServiceNow Integration Setup Guide

Complete step-by-step guide to integrate AEGIS with ServiceNow for automatic incident triage.

---

## Prerequisites

- ServiceNow instance (dev/test/prod)
- Admin or developer access
- AEGIS API endpoint accessible from ServiceNow (public URL or VPN)

---

## Step 1: Configure AEGIS Endpoint

Your AEGIS webhook endpoint is:
```
POST https://<your-aegis-server>:8080/webhook/servicenow
```

For EC2 deployment, ensure:
- Security Group allows inbound on port 8080
- Use ALB/nginx for HTTPS (recommended for production)

---

## Step 2: Create REST Message in ServiceNow

### 2.1 Navigate to REST Message

1. Go to **System Web Services → Outbound → REST Message**
2. Click **New**

### 2.2 Configure REST Message

| Field | Value |
|-------|-------|
| **Name** | AEGIS Triage Webhook |
| **Endpoint** | `https://<your-aegis-server>:8080/webhook/servicenow` |
| **Authentication** | No authentication (or Basic if you add auth) |

### 2.3 Add HTTP Request (Method)

1. In the **HTTP Methods** related list, click **New**
2. Configure:

| Field | Value |
|-------|-------|
| **Name** | POST |
| **HTTP Method** | POST |
| **Endpoint** | `${rest_message.endpoint}` |

3. In **HTTP Request** tab, add header:
   - **Name**: `Content-Type`
   - **Value**: `application/json`

4. In **Content** field, add the JSON payload template:

```json
{
    "number": "${number}",
    "short_description": "${short_description}",
    "description": "${description}",
    "caller_id": "${caller_id}",
    "category": "${category}",
    "subcategory": "${subcategory}",
    "cmdb_ci": "${cmdb_ci}",
    "priority": "${priority}",
    "sys_id": "${sys_id}"
}
```

5. Click **Submit**

---

## Step 3: Create Business Rule

### 3.1 Navigate to Business Rules

1. Go to **System Definition → Business Rules**
2. Click **New**

### 3.2 Configure Business Rule

**When tab:**

| Field | Value |
|-------|-------|
| **Name** | AEGIS AI Triage Trigger |
| **Table** | Incident [incident] |
| **Advanced** | ✅ Checked |
| **When** | async |
| **Insert** | ✅ Checked |
| **Update** | ☐ Unchecked |

**Condition:**
```
current.state == 1 && current.assignment_group.nil()
```

This triggers for:
- New incidents (state = 1)
- Not yet assigned to a group

### 3.3 Advanced Script

```javascript
(function executeRule(current, previous /*null when async*/) {

    // Only process new incidents without assignment
    if (current.state != 1 || !current.assignment_group.nil()) {
        return;
    }

    try {
        // Create REST request
        var restMessage = new sn_ws.RESTMessageV2('AEGIS Triage Webhook', 'POST');
        
        // Set endpoint variables
        restMessage.setStringParameterNoEscape('number', current.number.toString());
        restMessage.setStringParameterNoEscape('short_description', current.short_description.toString());
        restMessage.setStringParameterNoEscape('description', current.description.toString() || '');
        restMessage.setStringParameterNoEscape('caller_id', current.caller_id.getDisplayValue() || '');
        restMessage.setStringParameterNoEscape('category', current.category.toString() || '');
        restMessage.setStringParameterNoEscape('subcategory', current.subcategory.toString() || '');
        restMessage.setStringParameterNoEscape('cmdb_ci', current.cmdb_ci.getDisplayValue() || '');
        restMessage.setStringParameterNoEscape('priority', current.priority.toString() || '3');
        restMessage.setStringParameterNoEscape('sys_id', current.sys_id.toString());

        // Execute async - don't wait for response
        var response = restMessage.executeAsync();
        
        // Log the triage request
        gs.info('AEGIS: Triggered AI triage for ' + current.number);
        
    } catch (ex) {
        gs.error('AEGIS: Failed to trigger triage for ' + current.number + ': ' + ex.getMessage());
    }

})(current, previous);
```

### 3.4 Click Submit

---

## Step 4: Test the Integration

### 4.1 Create Test Incident

1. Go to **Incident → Create New**
2. Fill in:
   - **Caller**: Any user
   - **Short description**: "Cannot connect to VPN from home office"
   - **Description**: "User reports VPN client shows 'Connection timeout' error when trying to connect. Started happening after Windows update yesterday."
3. **Submit**

### 4.2 Verify in AEGIS

Check the API:
```bash
curl http://localhost:8080/status
```

Look for increased queue count.

### 4.3 Check Worker Logs

```bash
docker-compose logs --tail 50 aegis-worker
```

Look for:
```
📥 Processing: INC0012345
[GUARDRAILS] Scrubbed PII
[ENRICHMENT] Enriching...
[TRIAGE_LLM] Analyzing...
[EXECUTOR] Executing...
✅ Completed: INC0012345 -> executed
```

### 4.4 Verify ServiceNow Update

Go back to the incident - you should see:
- Work notes updated with AI analysis
- Category/Subcategory populated
- Assignment group set

---

## Step 5: Production Considerations

### 5.1 Add Condition Filters

Modify the Business Rule condition to exclude certain incidents:

```javascript
// Skip if already assigned or in certain states
if (!current.assignment_group.nil()) return;
if (current.state > 2) return;  // Skip if beyond New/In Progress

// Skip test incidents
if (current.short_description.toString().toLowerCase().indexOf('test') == 0) return;

// Skip VIP users (optional - or prioritize them)
// if (current.caller_id.vip == true) { ... special handling ... }
```

### 5.2 Add Retry Logic

For production, add retry in case of network issues:

```javascript
var maxRetries = 3;
var retryDelay = 1000; // ms

for (var attempt = 1; attempt <= maxRetries; attempt++) {
    try {
        var response = restMessage.execute();
        if (response.getStatusCode() == 200 || response.getStatusCode() == 202) {
            gs.info('AEGIS: Successfully triggered for ' + current.number);
            break;
        }
    } catch (ex) {
        if (attempt == maxRetries) {
            gs.error('AEGIS: All retries failed for ' + current.number);
        } else {
            gs.warn('AEGIS: Retry ' + attempt + ' for ' + current.number);
            gs.sleep(retryDelay * attempt);
        }
    }
}
```

### 5.3 Rate Limiting

For incident storms, add throttling in AEGIS:
- The webhook already returns queue position
- Storm Shield (duplicate detection) prevents redundant processing
- Kill switch can halt all processing if needed

---

## Troubleshooting

### Issue: Business Rule Not Triggering

1. Check Business Rule is **Active**
2. Verify condition matches (state = 1, no assignment group)
3. Check **System Logs → Application Logs** for errors

### Issue: 404 from AEGIS

1. Verify endpoint URL is correct
2. Check AEGIS API is running: `curl http://your-server:8080/health`
3. Check firewall/security group allows traffic

### Issue: Timeout

1. Increase timeout in REST Message settings
2. Use `executeAsync()` instead of `execute()`

### Issue: Empty Response

1. Check worker is running: `docker ps | grep worker`
2. Check worker logs for processing
3. Verify Redis connection

---

## API Reference

### Webhook Request Format

```json
{
    "number": "INC0012345",
    "short_description": "Cannot connect to VPN",
    "description": "Full description...",
    "caller_id": "john.doe",
    "category": "Network",
    "subcategory": "",
    "cmdb_ci": "VPN Server 01",
    "priority": "3"
}
```

### Webhook Response

```json
{
    "status": "queued",
    "incident_number": "INC0012345",
    "triage_id": "TRG202602051030001234",
    "queue_position": 1,
    "message": "Incident queued for AI triage"
}
```

### Check Triage Result

```bash
GET /triage/{triage_id}
```

Returns full triage result including classification, reasoning, and actions taken.

---

## Next Steps

1. ✅ Create REST Message
2. ✅ Create Business Rule  
3. ✅ Test with sample incident
4. 🔄 Configure N8N workflow for advanced orchestration (optional)
5. 🔄 Set up monitoring dashboards
