import jsQR from 'jsqr'

/**
 * Decode QR code from canvas image data
 * @param {ImageData} imageData - Canvas image data
 * @returns {object|null} - Decoded QR data or null if not found
 */
export const decodeQRFromImageData = (imageData) => {
  try {
    return jsQR(imageData.data, imageData.width, imageData.height)
  } catch (error) {
    console.error('Error decoding QR code:', error)
    return null
  }
}

/**
 * Decode QR code from canvas element
 * @param {HTMLCanvasElement} canvas - Canvas element with QR code image
 * @returns {object|null} - Decoded QR data with data and location properties
 */
export const decodeQRFromCanvas = (canvas) => {
  try {
    const ctx = canvas.getContext('2d')
    if (!ctx) return null
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    return decodeQRFromImageData(imageData)
  } catch (error) {
    console.error('Error decoding QR from canvas:', error)
    return null
  }
}

/**
 * Decode QR code from an image element
 * @param {HTMLImageElement} img - Image element
 * @returns {Promise<object|null>} - Promise resolving to decoded QR data or null
 */
export const decodeQRFromImage = async (img) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    canvas.width = img.width
    canvas.height = img.height
    
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      resolve(null)
      return
    }
    
    ctx.drawImage(img, 0, 0)
    resolve(decodeQRFromCanvas(canvas))
  })
}

/**
 * Decode QR code from a blob (file)
 * @param {Blob} blob - Image blob
 * @returns {Promise<object|null>} - Promise resolving to decoded QR data or null
 */
export const decodeQRFromBlob = async (blob) => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = async (e) => {
      const img = new Image()
      img.onload = async () => {
        const result = await decodeQRFromImage(img)
        resolve(result)
      }
      img.onerror = () => resolve(null)
      img.src = e.target.result
    }
    reader.onerror = () => resolve(null)
    reader.readAsDataURL(blob)
  })
}

/**
 * Extract text from decoded QR data
 * @param {object} decodedQR - Decoded QR data from jsQR
 * @returns {string} - Extracted text/URL
 */
export const extractQRText = (decodedQR) => {
  return decodedQR?.data || ''
}

/**
 * Check if decoded QR contains a valid URL
 * @param {object} decodedQR - Decoded QR data
 * @returns {boolean} - True if contains URL
 */
export const isQRURL = (decodedQR) => {
  const text = extractQRText(decodedQR)
  try {
    new URL(text)
    return true
  } catch {
    return text.startsWith('http://') || text.startsWith('https://')
  }
}

/**
 * Ensure URL has protocol
 * @param {string} url - URL string
 * @returns {string} - URL with protocol
 */
export const ensureURLProtocol = (url) => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return 'https://' + url
}
