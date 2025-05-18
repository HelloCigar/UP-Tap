export function useCameraCapture() {
    // Holds the File object returned from the input
    const photoFile = ref<File | null>(null);
    // Object URL for previewing the image
    const photoURL = ref<string | null>(null);
  
    // Programmatically trigger the hidden file input
    let inputEl: HTMLInputElement | null = null;
    const openCamera = () => {
      if (!inputEl) {
        inputEl = document.createElement('input');
        inputEl.type = 'file';
        inputEl.accept = 'image/*';
        inputEl.capture = 'environment';
        inputEl.style.display = 'none';
        inputEl.addEventListener('change', onFileChange);
        document.body.appendChild(inputEl);
      }
      inputEl.click();
    };
  
    // Handle file selection
    function onFileChange(this: HTMLInputElement) {
      const files = this.files;
      if (files && files[0]) {
        photoFile.value = files[0];
        // Revoke old URL
        if (photoURL.value) URL.revokeObjectURL(photoURL.value);
        photoURL.value = URL.createObjectURL(files[0]);
      }
      // Reset input for next capture
      this.value = '';
    }
  
    // Clean up on unmount
    onUnmounted(() => {
      if (inputEl) {
        inputEl.removeEventListener('change', onFileChange);
        document.body.removeChild(inputEl);
        inputEl = null;
      }
      if (photoURL.value) {
        URL.revokeObjectURL(photoURL.value);
      }
    });
  
    return {
      photoFile,
      photoURL,
      openCamera,
    };
  }