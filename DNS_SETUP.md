# DNS Setup Guide - Changing Nameservers to Vercel

## What You're Doing
You're telling your domain registrar (Porkbun) to use Vercel's nameservers instead of Porkbun's. This lets Vercel manage all DNS records automatically.

## Step-by-Step Instructions

### Step 1: Log into Porkbun
1. Go to **https://porkbun.com**
2. Click **"Log In"** in the top right
3. Enter your email and password

### Step 2: Find Your Domain
1. Once logged in, you'll see your account dashboard
2. Look for **"epsteinbase.xyz"** in your domain list
3. Click on **"epsteinbase.xyz"** (or the domain name itself)

### Step 3: Navigate to Nameservers
You should see several tabs/sections. Look for one of these:
- **"Nameservers"** tab (most common)
- **"DNS"** tab → then look for Nameservers section
- Or a section directly labeled **"Nameservers"**

### Step 4: Edit Nameservers
1. You'll see your current nameservers listed (probably 4 Porkbun ones like):
   - `curitiba.ns.porkbun.com`
   - `fortaleza.ns.porkbun.com`
   - `maceio.ns.porkbun.com`
   - `salvador.ns.porkbun.com`

2. Look for an **"Edit"**, **"Change"**, or **pencil icon** button
3. Click it to enter edit mode

### Step 5: Replace with Vercel Nameservers
**IMPORTANT**: You'll see multiple input fields (maybe 4-5). Do this:

1. **Delete/Clear ALL existing nameservers** from all fields
2. **In the FIRST field**, enter: `ns1.vercel-dns.com`
3. **In the SECOND field**, enter: `ns2.vercel-dns.com`
4. **Leave all other fields EMPTY/BLANK** (don't add anything to fields 3, 4, 5, etc.)

**You should only have 2 nameservers total:**
```
Field 1: ns1.vercel-dns.com
Field 2: ns2.vercel-dns.com
Field 3: (leave blank)
Field 4: (leave blank)
```

### Step 6: Save Changes
1. Click **"Save"**, **"Update"**, or **"Submit"** button
2. Confirm the change if a popup appears
3. You might see a warning - that's normal, confirm anyway

### Step 7: Wait for DNS Propagation
- DNS changes take time to propagate globally
- Usually works within **1-2 hours**
- Can take up to **48 hours** in rare cases
- Vercel will automatically detect when DNS is ready
- **You'll receive an email from Vercel** when the domain is verified and ready

## What Happens Next?
- Vercel automatically creates all necessary DNS records
- Your domain will work at **https://epsteinbase.xyz**
- No need to manually add A records, CNAMEs, etc.
- Vercel manages everything automatically

## Troubleshooting

**"Can't find Nameservers section":**
- Try looking in the "DNS" or "Advanced DNS" tab
- Some registrars call it "DNS Nameservers" or "NS Records"

**"Won't let me leave fields blank":**
- Some systems require exactly 2 nameservers, which is fine
- Just make sure you only have the 2 Vercel ones

**"Changes not working after a few hours":**
- Check if nameservers saved correctly
- Wait up to 48 hours for full propagation
- Check Vercel dashboard for verification status

## Current Status
After changing nameservers, you can check status with:
```bash
vercel domains inspect epsteinbase.xyz
```


