import whois

def domain_whois(domain_or_email):
    """Get WHOIS information for a domain or email"""
    try:
        # Handle both domain and email inputs
        if '@' in domain_or_email:
            domain = domain_or_email.split('@')[1]
        else:
            domain = domain_or_email
            
        domain_info = whois.whois(domain)
        
        # Handle potential None values safely
        return {
            "Registrar": domain_info.registrar or "Unknown",
            "Creation Date": str(domain_info.creation_date) if domain_info.creation_date else "Unknown",
            "Expiration Date": str(domain_info.expiration_date) if domain_info.expiration_date else "Unknown",
            "Organization": domain_info.org or "Unknown"
        }
    except Exception as e:
        return {"Error": f"WHOIS lookup failed: {e}"}