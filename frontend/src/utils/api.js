/**
 * API Client with JWT token support
 */

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ? import.meta.env.VITE_API_URL : '';

class ApiClient {
  constructor() {
    this.token = null;
    this.loadToken();
  }

  /**
   * Load token from localStorage
   */
  loadToken() {
    this.token = localStorage.getItem('token');
  }

  /**
   * Set authentication token
   * @param {string} token - JWT token
   */
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  /**
   * Get authentication headers
   * @returns {Object} Headers object
   */
  getHeaders(contentType = 'application/json') {
    const headers = {};
    
    if (contentType) {
      headers['Content-Type'] = contentType;
    }
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  /**
   * Make API request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise} Response data
   */
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(options.contentType),
        ...options.headers,
      },
    };

    // Remove contentType from options to avoid issues
    delete config.contentType;

    try {
      const response = await fetch(url, config);
      
      // Handle 401 Unauthorized
      if (response.status === 401) {
        this.setToken(null);
        window.dispatchEvent(new Event('unauthorized'));
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise} Token and user data
   */
  async register(userData) {
    const data = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    
    return data;
  }

  /**
   * Login user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise} Token and user data
   */
  async login(email, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    
    return data;
  }

  /**
   * Get current user
   * @returns {Promise} User data
   */
  async getCurrentUser() {
    return await this.request('/api/auth/me');
  }

  /**
   * Refresh token
   * @returns {Promise} New token and user data
   */
  async refreshToken() {
    const data = await this.request('/api/auth/refresh', {
      method: 'POST',
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    
    return data;
  }

  /**
   * Logout user
   */
  logout() {
    this.setToken(null);
  }

  /**
   * Scan a document
   * @param {File} file - PDF file to scan
   * @param {number} confThreshold - Confidence threshold
   * @param {boolean} saveHistory - Save to history
   * @returns {Promise} Scan results
   */
  async scanDocument(file, confThreshold = 0.5, saveHistory = true) {
    const formData = new FormData();
    formData.append('file', file);
    
    const url = `/api/document-inspector/detect?conf_threshold=${confThreshold}&save_history=${saveHistory}`;
    
    return await this.request(url, {
      method: 'POST',
      body: formData,
      contentType: null, // Let browser set Content-Type for FormData
    });
  }

  /**
   * Get scan history
   * @param {number} skip - Number of records to skip
   * @param {number} limit - Maximum number of records
   * @returns {Promise} List of scans
   */
  async getScans(skip = 0, limit = 50) {
    return await this.request(`/api/scans/?skip=${skip}&limit=${limit}`);
  }

  /**
   * Get scan details
   * @param {number} scanId - Scan ID
   * @returns {Promise} Scan details
   */
  async getScanDetail(scanId) {
    return await this.request(`/api/scans/${scanId}`);
  }

  /**
   * Download scan PDF
   * @param {number} scanId - Scan ID
   * @returns {string} Download URL
   */
  getScanDownloadUrl(scanId) {
    return `${API_BASE_URL}/api/scans/${scanId}/download`;
  }

  /**
   * Delete scan
   * @param {number} scanId - Scan ID
   * @returns {Promise} Success message
   */
  async deleteScan(scanId) {
    return await this.request(`/api/scans/${scanId}`, {
      method: 'DELETE',
    });
  }

  async downloadScanPdf(scanId) {
    const endpoint = `/api/scans/${scanId}/download`;
    const url = API_BASE_URL ? `${API_BASE_URL}${endpoint}` : endpoint;
    const res = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders(null),
    });
    if (!res.ok) {
      let detail = 'Request failed';
      try {
        const d = await res.json();
        detail = d.detail || detail;
      } catch {}
      throw new Error(detail);
    }
    const cd = res.headers.get('content-disposition');
    let filename;
    if (cd) {
      const match = cd.match(/filename="?([^";]+)"?/i);
      if (match) filename = match[1];
    }
    const blob = await res.blob();
    return { blob, filename };
  }

  /**
   * Get scan statistics
   * @returns {Promise} User scan statistics
   */
  async getScanStats() {
    return await this.request('/api/scans/stats');
  }

  // Admin endpoints

  /**
   * Get all users (admin only)
   * @param {number} skip - Number of records to skip
   * @param {number} limit - Maximum number of records
   * @returns {Promise} List of users
   */
  async getUsers(skip = 0, limit = 50) {
    return await this.request(`/api/admin/users?skip=${skip}&limit=${limit}`);
  }

  /**
   * Get user's scans (admin only)
   * @param {number} userId - User ID
   * @param {number} skip - Number of records to skip
   * @param {number} limit - Maximum number of records
   * @returns {Promise} List of scans
   */
  async getUserScans(userId, skip = 0, limit = 50) {
    return await this.request(`/api/admin/users/${userId}/scans?skip=${skip}&limit=${limit}`);
  }

  /**
   * Get system stats (admin only)
   * @returns {Promise} System statistics
   */
  async getSystemStats() {
    return await this.request('/api/admin/stats');
  }

  /**
   * Delete user (admin only)
   * @param {number} userId - User ID
   * @returns {Promise} Success message
   */
  async deleteUser(userId) {
    return await this.request(`/api/admin/users/${userId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
export default new ApiClient();

