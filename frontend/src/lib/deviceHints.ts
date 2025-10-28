export function isMobileDevice() {
  try {
    return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent || '');
  } catch (e) {
    return false;
  }
}

export function isLowPowerDevice(): boolean {
  try {
    const nav = navigator as any;
    // saveData users want lightweight experiences
    if (nav.connection && nav.connection.saveData) return true;
    const et = nav.connection && nav.connection.effectiveType;
    if (et === '2g' || et === 'slow-2g') return true;
    // battery API: if present and low and not charging
    if (nav.getBattery) {
      // synchronous check isn't possible; return false as default and caller may poll
      return false;
    }
    return false;
  } catch (e) {
    return false;
  }
}
