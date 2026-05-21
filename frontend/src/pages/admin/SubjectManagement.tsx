import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Space, Popconfirm, Tag } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { adminAPI } from '../../api';

const SEMESTERS = ['1','2','3','4','5','6','7','8'];

const SubjectManagement: React.FC = () => {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form] = Form.useForm();

  const fetchSubjects = () => {
    setLoading(true);
    adminAPI.getSubjects().then(res => setSubjects(res.data.subjects))
      .catch(() => message.error('Failed to load')).finally(() => setLoading(false));
  };
  useEffect(() => { fetchSubjects(); }, []);

  const handleSubmit = async (values: any) => {
    try {
      if (editingId) { await adminAPI.updateSubject(editingId, values); message.success('Updated'); }
      else { await adminAPI.createSubject(values); message.success('Created'); }
      setModalOpen(false); form.resetFields(); setEditingId(null); fetchSubjects();
    } catch (err: any) { message.error(err.response?.data?.detail || 'Failed'); }
  };

  const columns = [
    { title: 'Code', dataIndex: 'subject_code', key: 'code' },
    { title: 'Name', dataIndex: 'subject_name', key: 'name' },
    { title: 'Department', dataIndex: 'department', key: 'dept' },
    { title: 'Semester', dataIndex: 'semester', key: 'sem', render: (v: string) => <Tag color="blue">Sem {v}</Tag> },
    { title: 'Actions', key: 'actions', render: (_: any, r: any) => (
      <Space>
        <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingId(r.id); form.setFieldsValue(r); setModalOpen(true); }} />
        <Popconfirm title="Delete?" onConfirm={async () => { await adminAPI.deleteSubject(r.id); message.success('Deleted'); fetchSubjects(); }}>
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      </Space>
    )},
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <h2>Subject Management</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingId(null); form.resetFields(); setModalOpen(true); }}>Add Subject</Button>
      </div>
      <Table dataSource={subjects} columns={columns} rowKey="id" loading={loading} />
      <Modal title={editingId ? 'Edit Subject' : 'Add Subject'} open={modalOpen}
             onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="subject_code" label="Subject Code" rules={[{ required: true }]}><Input disabled={!!editingId} /></Form.Item>
          <Form.Item name="subject_name" label="Subject Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="department" label="Department" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="semester" label="Semester" rules={[{ required: true }]}>
            <Select options={SEMESTERS.map(s => ({ value: s, label: `Semester ${s}` }))} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SubjectManagement;
