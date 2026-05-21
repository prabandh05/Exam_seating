import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Space, Popconfirm, Tag } from 'antd';
import { adminAPI } from '../../api';

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetch = () => {
    setLoading(true);
    adminAPI.getNotifications().then(res => setNotifications(res.data.notifications))
      .catch(() => message.error('Failed')).finally(() => setLoading(false));
  };
  useEffect(() => { fetch(); }, []);

  const handleSubmit = async (values: any) => {
    try {
      await adminAPI.createNotification(values);
      message.success('Created');
      setModalOpen(false); form.resetFields(); fetch();
    } catch (err: any) { message.error(err.response?.data?.detail || 'Failed'); }
  };

  const columns = [
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Type', dataIndex: 'type', key: 'type', render: (v: string) => <Tag>{v}</Tag> },
    { title: 'Target Role', dataIndex: 'target_role', key: 'role', render: (v: string) => v || 'All' },
    { title: 'Created At', dataIndex: 'created_at', key: 'date', render: (v: string) => new Date(v).toLocaleString() },
    { title: 'Actions', key: 'actions', render: (_: any, r: any) => (
      <Popconfirm title="Delete?" onConfirm={async () => { await adminAPI.deleteNotification(r.id); message.success('Deleted'); fetch(); }}>
        <Button type="link" danger>Delete</Button>
      </Popconfirm>
    )},
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <h2>Notifications</h2>
        <Button type="primary" onClick={() => { form.resetFields(); setModalOpen(true); }}>Send Notification</Button>
      </div>
      <Table dataSource={notifications} columns={columns} rowKey="id" loading={loading} />
      
      <Modal title="Send Notification" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="title" label="Title" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="message" label="Message" rules={[{ required: true }]}><Input.TextArea rows={4} /></Form.Item>
          <Form.Item name="type" label="Type" rules={[{ required: true }]} initialValue="general">
            <Select options={['exam', 'seating', 'hall_change', 'attendance', 'general'].map(v => ({ label: v, value: v }))} />
          </Form.Item>
          <Form.Item name="target_role" label="Target Role">
            <Select options={[{ label: 'All', value: '' }, { label: 'Student', value: 'student' }, { label: 'Invigilator', value: 'invigilator' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default NotificationsPage;
