import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Switch, message, Space, Popconfirm, Tag } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { adminAPI } from '../../api';

const HallManagement: React.FC = () => {
  const [halls, setHalls] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form] = Form.useForm();

  const fetch = () => {
    setLoading(true);
    adminAPI.getHalls().then(res => setHalls(res.data.halls))
      .catch(() => message.error('Failed')).finally(() => setLoading(false));
  };
  useEffect(() => { fetch(); }, []);

  const handleSubmit = async (values: any) => {
    try {
      if (editingId) { await adminAPI.updateHall(editingId, values); message.success('Updated'); }
      else { await adminAPI.createHall(values); message.success('Created'); }
      setModalOpen(false); form.resetFields(); setEditingId(null); fetch();
    } catch (err: any) { message.error(err.response?.data?.detail || 'Failed'); }
  };

  const handleToggle = async (id: number, enabled: boolean) => {
    await adminAPI.toggleHall(id, { is_enabled: enabled });
    message.success(enabled ? 'Enabled' : 'Disabled');
    fetch();
  };

  const columns = [
    { title: 'Hall No', dataIndex: 'hall_number', key: 'hall' },
    { title: 'Floor', dataIndex: 'floor_number', key: 'floor' },
    { title: 'Capacity', dataIndex: 'capacity', key: 'cap' },
    { title: 'Layout', key: 'layout', render: (_: any, r: any) => `${r.num_rows}R × ${r.num_columns}C` },
    { title: 'Benches', dataIndex: 'num_benches', key: 'benches' },
    { title: 'Status', key: 'status', render: (_: any, r: any) => (
      <Switch checked={r.is_enabled} onChange={(v) => handleToggle(r.id, v)}
              checkedChildren="Enabled" unCheckedChildren="Disabled" />
    )},
    { title: 'Actions', key: 'actions', render: (_: any, r: any) => (
      <Space>
        <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingId(r.id); form.setFieldsValue(r); setModalOpen(true); }} />
        <Popconfirm title="Delete?" onConfirm={async () => { await adminAPI.deleteHall(r.id); message.success('Deleted'); fetch(); }}>
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      </Space>
    )},
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <h2>Hall Management</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingId(null); form.resetFields(); setModalOpen(true); }}>Add Hall</Button>
      </div>
      <Table dataSource={halls} columns={columns} rowKey="id" loading={loading} />
      <Modal title={editingId ? 'Edit Hall' : 'Add Hall'} open={modalOpen}
             onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="hall_number" label="Hall Number" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="floor_number" label="Floor" rules={[{ required: true }]}><InputNumber min={0} max={20} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="num_rows" label="Rows" rules={[{ required: true }]}><InputNumber min={1} max={50} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="num_columns" label="Columns" rules={[{ required: true }]}><InputNumber min={1} max={50} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="capacity" label="Capacity" rules={[{ required: true }]}><InputNumber min={1} max={500} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="num_benches" label="Benches" rules={[{ required: true }]}><InputNumber min={1} max={500} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default HallManagement;
