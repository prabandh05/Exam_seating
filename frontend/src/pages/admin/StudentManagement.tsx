import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Space, Upload, Tag, InputNumber, Popconfirm } from 'antd';
import { PlusOutlined, UploadOutlined, SearchOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { adminAPI } from '../../api';

const SEMESTERS = ['1','2','3','4','5','6','7','8'];
const GENDERS = ['male','female','other'];

const StudentManagement: React.FC = () => {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [search, setSearch] = useState('');
  const [filterDept, setFilterDept] = useState<string>();
  const [filterSem, setFilterSem] = useState<string>();
  const [form] = Form.useForm();

  const fetchStudents = () => {
    setLoading(true);
    adminAPI.getStudents({ page, page_size: 20, search, department: filterDept, semester: filterSem })
      .then(res => { setStudents(res.data.students); setTotal(res.data.total); })
      .catch(() => message.error('Failed to load students'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchStudents(); }, [page, search, filterDept, filterSem]);

  const handleSubmit = async (values: any) => {
    try {
      if (editingId) {
        const { password, register_number, ...updateData } = values;
        await adminAPI.updateStudent(editingId, updateData);
        message.success('Student updated');
      } else {
        await adminAPI.createStudent(values);
        message.success('Student created');
      }
      setModalOpen(false); form.resetFields(); setEditingId(null); fetchStudents();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (record: any) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await adminAPI.deleteStudent(id);
      message.success('Student deleted');
      fetchStudents();
    } catch { message.error('Delete failed'); }
  };

  const handleBulkUpload = async (file: File) => {
    try {
      const res = await adminAPI.bulkUpload(file);
      message.success(`Uploaded: ${res.data.successful} successful, ${res.data.failed} failed`);
      fetchStudents();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Upload failed');
    }
    return false;
  };

  const columns = [
    { title: 'Register No', dataIndex: 'register_number', key: 'register_number', sorter: true },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Department', dataIndex: 'department', key: 'department' },
    { title: 'Semester', dataIndex: 'semester', key: 'semester', render: (v: string) => <Tag color="blue">Sem {v}</Tag> },
    { title: 'Section', dataIndex: 'section', key: 'section' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Status', dataIndex: 'is_active', key: 'status', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? 'Active' : 'Inactive'}</Tag> },
    {
      title: 'Actions', key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Delete this student?" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <h2>Student Management</h2>
        <Space>
          <Upload beforeUpload={handleBulkUpload} showUploadList={false} accept=".csv,.xlsx,.xls">
            <Button icon={<UploadOutlined />}>Bulk Upload</Button>
          </Upload>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingId(null); form.resetFields(); setModalOpen(true); }}>
            Add Student
          </Button>
        </Space>
      </div>

      <Space style={{ marginBottom: 16 }}>
        <Input prefix={<SearchOutlined />} placeholder="Search..." value={search}
               onChange={e => { setSearch(e.target.value); setPage(1); }} allowClear style={{ width: 250 }} />
        <Select placeholder="Department" allowClear style={{ width: 150 }} onChange={v => { setFilterDept(v); setPage(1); }}
                options={[...new Set(students.map(s => s.department))].map(d => ({ value: d, label: d }))} />
        <Select placeholder="Semester" allowClear style={{ width: 120 }} onChange={v => { setFilterSem(v); setPage(1); }}
                options={SEMESTERS.map(s => ({ value: s, label: `Sem ${s}` }))} />
      </Space>

      <Table dataSource={students} columns={columns} rowKey="id" loading={loading}
             pagination={{ current: page, total, pageSize: 20, onChange: setPage }} />

      <Modal title={editingId ? 'Edit Student' : 'Add Student'} open={modalOpen}
             onCancel={() => { setModalOpen(false); setEditingId(null); }} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="register_number" label="Register Number" rules={[{ required: true }]}>
            <Input disabled={!!editingId} />
          </Form.Item>
          <Form.Item name="name" label="Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="department" label="Department" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="semester" label="Semester" rules={[{ required: true }]}>
            <Select options={SEMESTERS.map(s => ({ value: s, label: `Semester ${s}` }))} />
          </Form.Item>
          <Form.Item name="section" label="Section" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="year" label="Year" rules={[{ required: true }]}>
            <InputNumber min={1} max={4} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}><Input /></Form.Item>
          <Form.Item name="phone" label="Phone" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="gender" label="Gender" rules={[{ required: true }]}>
            <Select options={GENDERS.map(g => ({ value: g, label: g.charAt(0).toUpperCase() + g.slice(1) }))} />
          </Form.Item>
          {!editingId && (
            <Form.Item name="password" label="Password" rules={[{ required: true, min: 6 }]}>
              <Input.Password />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default StudentManagement;
