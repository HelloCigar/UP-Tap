export function useMobile() {
    const isMobile = ref(false)
  
    const checkIfMobile = () => {
      // Determine mobile by width
      const isMobileByWidth = window.innerWidth <= 768
      // Determine mobile by user agent
      const isMobileByUserAgent = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      )
      isMobile.value = isMobileByWidth || isMobileByUserAgent
    }
  
    onMounted(() => {
      checkIfMobile()
      window.addEventListener('resize', checkIfMobile)
    })
  
    onUnmounted(() => {
      window.removeEventListener('resize', checkIfMobile)
    })
  
    return { isMobile }
  }
  