export function isTokenExpired(token: string): boolean {
  if (!token) return true;
  try {
    const payloadBase64 = token.split('.')[1];
    if (!payloadBase64) return true;
    
    // JWT base64 uses url-safe chars '-' and '_' instead of '+' and '/'
    const base64 = payloadBase64.replace(/-/g, '+').replace(/_/g, '/');
    
    const decodedJson = atob(base64);
    const payload = JSON.parse(decodedJson);
    
    if (!payload.exp) return false;
    
    // Add a 10 second buffer
    const expTime = payload.exp * 1000;
    return Date.now() >= expTime - 10000;
  } catch (e) {
    return true; 
  }
}
