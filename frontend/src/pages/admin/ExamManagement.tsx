import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, DatePicker, TimePicker, message, Space, Tag, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { adminAPI } from '../../api';
import dayjs from 'dayjs';

const SEMESTERS = ['1','2','3','4','5','6','7','8'];
const EXAM_TYPES = ['internal','external','supplementary','midterm'];
const STATUSES = ['draft','published','ongoing','completed','cancelled'];
const STATUS_COLORS: Record<string, string> = { draft: 'default', published: 'blue', ongoing: 'green', completed: 'purple', cancelled: 'red' };

const ExamManagement: React.FC = () => {
  const [exams, setExams] = useState<any[]>([]);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>();
  const [form] = Form.useForm();

  const fetchExams = () => {
    setLoading(true);
    adminAPI.getExams({ page, page_size: 20, status: statusFilter })
      .then(res => { setExams(res.data.exams); setTotal(res.data.total); })
      .catch(() => message.error('Failed')).finally(() => setLoading(false));
  };

  useEffect(() => { fetchExams(); }, [page, statusFilter]);
  useEffect(() => { adminAPI.getSubjects().then(res => setSubjects(res.data.subjects)).catch(() => {}); }, []);

  const handleSubmit = async (values: any) => {
    try {
      const payload = {
        ...values,
        exam_date: values.exam_date.format('YYYY-MM-DD'),
        start_time: values.start_time.format('HH:mm:ss'),
        end_time: values.end_time.format('HH:mm:ss'),
      };
      if (editingId) { await adminAPI.updateExam(editingId, payload); message.success('Updated'); }
      else { await adminAPI.createExam(payload); message.success('Created'); }
      setModalOpen(false); form.resetFields(); setEditingId(null); fetchExams();
    } catch (err: any) { message.error(err.response?.data?.detail || 'Failed'); }
  };

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await adminAPI.updateExamStatus(id, { status });
      message.success(`Status updated to ${status}`);
      fetchExams();
    } catch (err: any) { message.error(err.response?.data?.detail || 'Failed'); }
  };

  const columns = [
    { title: 'Subject', key: 'subject', render: (_: any, r: any) => `${r.subject_name} (${r.subject_code})` },
    { title: 'Date', dataIndex: 'exam_date', key: 'date' },
    { title: 'Time', key: 'time', render: (_: any, r: any) => `${r.start_time} - ${r.end_time}` },
    { title: 'Type', dataIndex: 'exam_type', key: 'type', render: (v: string) => <Tag>{v.toUpperCase()}</Tag> },
    { title: 'Dept', dataIndex: 'department', key: 'dept' },
    { title: 'Sem', dataIndex: 'semester', key: 'sem' },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={STATUS_COLORS[v]}>{v.toUpperCase()}</Tag> },
    { title: 'Students', dataIndex: 'total_students_assigned', key: 'students' },
    { title: 'Actions', key: 'actions', render: (_: any, r: any) => (
      <Space>
        {r.status === 'draft' && <Button size="small" type="link" icon={<CheckCircleOutlined />} onClick={() => handleStatusChange(r.id, 'published')}>Publish</Button>}
        <Button type="link" icon={<EditOutlined />} onClick={() => {
          setEditingId(r.id);
          form.setFieldsValue({
            ...r, exam_date: dayjs(r.exam_date),
            start_time: dayjs(r.start_time, 'HH:mm:ss'), end_time: dayjs(r.end_time, 'HH:mm:ss'),
          });
          setModalOpen(true);
        }} />
        <Popconfirm title="Delete?" onConfirm={async () => { await adminAPI.deleteExam(r.id); message.success('Deleted'); fetchExams(); }}>
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      </Space>
    )},
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <h2>Exam Management</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingId(null); form.resetFields(); setModalOpen(true); }}>Create Exam</Button>
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Select placeholder="Filter Status" allowClear style={{ width: 150 }} onChange={v => { setStatusFilter(v); setPage(1); }}
                options={STATUSES.map(s => ({ value: s, label: s.toUpperCase() }))} />
      </Space>
      <Table dataSource={exams} columns={columns} rowKey="id" loading={loading}
             pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />
      <Modal title={editingId ? 'Edit Exam' : 'Create Exam'} open={modalOpen}
             onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="subject_id" label="Subject" rules={[{ required: true }]}>
            <Select showSearch optionFilterProp="label"
                    options={subjects.map((s: any) => ({ value: s.id, label: `${s.subject_name} (${s.subject_code})` }))} />
          </Form.Item>
          <Form.Item name="exam_date" label="Date" rules={[{ required: true }]}><DatePicker style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="start_time" label="Start Time" rules={[{ required: true }]}><TimePicker format="HH:mm" style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="end_time" label="End Time" rules={[{ required: true }]}><TimePicker format="HH:mm" style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="exam_type" label="Type" rules={[{ required: true }]}>
            <Select options={EXAM_TYPES.map(t => ({ value: t, label: t.toUpperCase() }))} />
          </Form.Item>
          <Form.Item name="department" label="Department" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="semester" label="Semester" rules={[{ required: true }]}>
            <Select options={SEMESTERS.map(s => ({ value: s, label: `Semester ${s}` }))} />
          </Form.Item>
          {!editingId && <Form.Item name="status" label="Status" initialValue="draft">
            <Select options={[{ value: 'draft', label: 'Draft' }, { value: 'published', label: 'Published' }]} />
          </Form.Item>}
        </Form>
      </Modal>
    </div>
  );
};

export default ExamManagement;
