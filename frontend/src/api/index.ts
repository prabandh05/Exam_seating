/**
 * API Service Layer — Centralized Axios instance with JWT interceptor.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ─── Auth ───
export const authAPI = {
  login: (data: { username: string; password: string; role: string }) =>
    api.post('/auth/login', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
};

// ─── Admin ───
export const adminAPI = {
  dashboardStats: () => api.get('/admin/dashboard/stats'),
  // Students
  getStudents: (params?: any) => api.get('/admin/students', { params }),
  createStudent: (data: any) => api.post('/admin/students', data),
  getStudent: (id: number) => api.get(`/admin/students/${id}`),
  updateStudent: (id: number, data: any) => api.put(`/admin/students/${id}`, data),
  deleteStudent: (id: number) => api.delete(`/admin/students/${id}`),
  bulkUpload: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return api.post('/admin/students/bulk-upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // Subjects
  getSubjects: (params?: any) => api.get('/admin/subjects', { params }),
  createSubject: (data: any) => api.post('/admin/subjects', data),
  updateSubject: (id: number, data: any) => api.put(`/admin/subjects/${id}`, data),
  deleteSubject: (id: number) => api.delete(`/admin/subjects/${id}`),
  // Halls
  getHalls: (params?: any) => api.get('/admin/halls', { params }),
  createHall: (data: any) => api.post('/admin/halls', data),
  getHall: (id: number) => api.get(`/admin/halls/${id}`),
  updateHall: (id: number, data: any) => api.put(`/admin/halls/${id}`, data),
  deleteHall: (id: number) => api.delete(`/admin/halls/${id}`),
  toggleHall: (id: number, data: { is_enabled: boolean }) =>
    api.patch(`/admin/halls/${id}/toggle`, data),
  // Exams
  getExams: (params?: any) => api.get('/admin/exams', { params }),
  createExam: (data: any) => api.post('/admin/exams', data),
  getExam: (id: number) => api.get(`/admin/exams/${id}`),
  updateExam: (id: number, data: any) => api.put(`/admin/exams/${id}`, data),
  deleteExam: (id: number) => api.delete(`/admin/exams/${id}`),
  updateExamStatus: (id: number, data: { status: string }) =>
    api.patch(`/admin/exams/${id}/status`, data),
  // Seating
  generateSeating: (data: any) => api.post('/admin/seating/generate', data),
  getSeating: (examId: number) => api.get(`/admin/seating/${examId}`),
  swapSeats: (data: any) => api.post('/admin/seating/swap', data),
  lockSeat: (id: number, data: { is_locked: boolean }) =>
    api.patch(`/admin/seating/${id}/lock`, data),
  clearSeating: (examId: number) => api.delete(`/admin/seating/${examId}`),
  checkConflicts: (examId: number) => api.get(`/admin/seating/${examId}/conflicts`),
  getHallLayout: (hallId: number, examId: number) =>
    api.get(`/admin/seating/halls/${hallId}/layout`, { params: { exam_id: examId } }),
  manualAssignSeat: (data: any) => api.post('/admin/seating/assign', data),
  manualRemoveSeat: (seatingId: number) => api.delete(`/admin/seating/remove/${seatingId}`),
  // Invigilators
  getInvigilators: (params?: any) => api.get('/admin/invigilators', { params }),
  createInvigilator: (data: any) => api.post('/admin/invigilators', data),
  getInvigilator: (id: number) => api.get(`/admin/invigilators/${id}`),
  updateInvigilator: (id: number, data: any) => api.put(`/admin/invigilators/${id}`, data),
  deleteInvigilator: (id: number) => api.delete(`/admin/invigilators/${id}`),
  assignDuty: (data: any) => api.post('/admin/invigilators/assign', data),
  autoAssignDuties: (examId: number) =>
    api.post(`/admin/invigilators/auto-assign?exam_id=${examId}`),
  // Attendance
  getAttendance: (examId: number) => api.get(`/admin/attendance/${examId}`),
  // Notifications
  getNotifications: () => api.get('/admin/notifications'),
  createNotification: (data: any) => api.post('/admin/notifications', data),
  deleteNotification: (id: number) => api.delete(`/admin/notifications/${id}`),
  // Audit Logs
  getAuditLogs: (params?: any) => api.get('/admin/audit-logs', { params }),
  // Reports
  exportSeatingExcel: (examId: number) =>
    api.get(`/admin/reports/seating/${examId}/excel`, { responseType: 'blob' }),
  exportAttendanceExcel: (examId: number) =>
    api.get(`/admin/reports/attendance/${examId}/excel`, { responseType: 'blob' }),
};

// ─── Invigilator ───
export const invigilatorAPI = {
  dashboard: () => api.get('/invigilator/dashboard'),
  getDuties: () => api.get('/invigilator/duties'),
  getDutySeating: (dutyId: number) => api.get(`/invigilator/duties/${dutyId}/seating`),
  markAttendance: (dutyId: number, data: any) =>
    api.post(`/invigilator/attendance/${dutyId}`, data),
  completeDuty: (dutyId: number) =>
    api.post(`/invigilator/duties/${dutyId}/complete`),
  getProfile: () => api.get('/invigilator/profile'),
};

// ─── Student ───
export const studentAPI = {
  dashboard: () => api.get('/student/dashboard'),
  getExams: () => api.get('/student/exams'),
  getSeating: () => api.get('/student/seating'),
  getNotifications: () => api.get('/student/notifications'),
  markNotificationRead: (id: number) => api.patch(`/student/notifications/${id}/read`),
};

export default api;
