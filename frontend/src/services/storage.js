const DEVICE_ID_KEY = 'b2_device_id';
const STUDENT_NAME_KEY = 'b2_student_name';

export function getDeviceId() {
  let id = localStorage.getItem(DEVICE_ID_KEY);
  if (!id) {
    id = 'std_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now().toString(36);
    localStorage.setItem(DEVICE_ID_KEY, id);
  }
  return id;
}

export function getStudentName() {
  return localStorage.getItem(STUDENT_NAME_KEY) || '';
}

export function setStudentName(name) {
  const clean = (name || '').trim();
  if (clean) {
    localStorage.setItem(STUDENT_NAME_KEY, clean);
  } else {
    localStorage.removeItem(STUDENT_NAME_KEY);
  }
}
