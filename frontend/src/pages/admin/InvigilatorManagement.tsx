import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Space, Popconfirm, Tag } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { adminAPI } from '../../api';

const InvigilatorManagement: React.FC = () => {
  const [invigilators, setInvigilators] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form] = Form.useForm();
  
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [assignForm] = Form.useForm();
  const [exams, setExams] = useState<any[]>([]);
  const [halls, setHalls] = useState<any[]>([]);
  const [hallExams, setHallExams] = useState<any[]>([]);

  const fetchInvigilators = () => {
    setLoading(true);
    adminAPI.getInvigilators().then(res => setInvigilators(res.data.invigilators))
      .catch(() => message.error('Failed')).finally(() => setLoading(false));
  };

  useEffect(() => { 
    fetchInvigilators(); 
    adminAPI.getExams({ status: 'published' }).then(res => setExams(res.data.exams));
    adminAPI.getHalls({ is_enabled: true }).then(res => setHalls(res.data.halls));
  }, []);

  const handleSubmit = async (values: any) => {
    try {
      if (editingId) { await adminAPI.updateInvigilator(editingId, values); message.success('Updated'); }
      else { await adminAPI.createInvigilator(values); message.success('Created'); }
      setModalOpen(false); form.resetFields(); setEditingId(null); fetchInvigilators();
    } catch (err: any) { message.error(err.response?.data?.detail || 'Failed'); }
  };

  const handleAssignSubmit = async (values: any) => {
    try {
      const selectedExams = exams.filter(e => values.exam_ids.includes(e.id));
      const uniqueSlots = new Set(selectedExams.map(e => `${e.exam_date}|${e.start_time}|${e.end_time}`));
      
      for (const slot of uniqueSlots) {
        const [exam_date, start_time, end_time] = slot.split('|');
        const payload = {
          invigilator_id: values.invigilator_id,
          hall_id: values.hall_id,
          exam_date,
          start_time,
          end_time
        };
        await adminAPI.assignDuty(payload);
      }
      message.success('Duty assigned successfully');
      setAssignModalOpen(false);
      assignForm.resetFields();
      setHallExams([]);
    } catch (err: any) { message.error(err.response?.data?.detail || 'Assignment failed'); }
  };

  const handleHallChange = (hallId: number) => {
    assignForm.setFieldsValue({ exam_ids: [] });
    setHallExams([]);
    adminAPI.getHallExams(hallId)
      .then(res => setHallExams(res.data.exams))
      .catch(() => message.error('Failed to fetch exams for this hall'));
  };

  const columns = [
    { title: 'ID', dataIndex: 'invigilator_id', key: 'id' },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Department', dataIndex: 'department', key: 'dept' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Phone', dataIndex: 'phone', key: 'phone' },
    { title: 'Status', dataIndex: 'is_active', key: 'status', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? 'Active' : 'Inactive'}</Tag> },
    { title: 'Duties', dataIndex: 'total_duties', key: 'duties' },
    { title: 'Actions', key: 'actions', render: (_: any, r: any) => (
      <Space>
        <Button size="small" onClick={() => { 
          assignForm.resetFields();
          setHallExams([]);
          assignForm.setFieldsValue({ invigilator_id: r.id }); 
          setAssignModalOpen(true); 
        }}>Assign Duty</Button>
        <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingId(r.id); form.setFieldsValue(r); setModalOpen(true); }} />
        <Popconfirm title="Delete?" onConfirm={async () => { await adminAPI.deleteInvigilator(r.id); message.success('Deleted'); fetchInvigilators(); }}>
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      </Space>
    )},
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <h2>Invigilator Management</h2>
        <Space>
          <Button onClick={() => {
            if(!exams.length) return message.warning('No published exams');
            adminAPI.autoAssignDuties(exams[0].id).then(res => message.success(res.data.message)).catch(err => message.error(err.response?.data?.detail));
          }}>Auto Assign</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingId(null); form.resetFields(); setModalOpen(true); }}>Add Invigilator</Button>
        </Space>
      </div>
      <Table dataSource={invigilators} columns={columns} rowKey="id" loading={loading} />
      
      <Modal title={editingId ? 'Edit Invigilator' : 'Add Invigilator'} open={modalOpen}
             onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="invigilator_id" label="Invigilator ID" rules={[{ required: true }]}><Input disabled={!!editingId} /></Form.Item>
          <Form.Item name="name" label="Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="department" label="Department" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}><Input /></Form.Item>
          <Form.Item name="phone" label="Phone" rules={[{ required: true }]}><Input /></Form.Item>
          {!editingId && <Form.Item name="password" label="Password" rules={[{ required: true, min: 6 }]}><Input.Password /></Form.Item>}
        </Form>
      </Modal>

      <Modal title="Assign Duty" open={assignModalOpen} onCancel={() => setAssignModalOpen(false)} onOk={() => assignForm.submit()}>
        <Form form={assignForm} layout="vertical" onFinish={handleAssignSubmit}>
          <Form.Item name="invigilator_id" hidden><Input /></Form.Item>
          <Form.Item name="hall_id" label="Hall" rules={[{ required: true }]}>
             <Select 
               options={halls.map(h => ({ label: h.hall_number, value: h.id }))} 
               onChange={handleHallChange}
             />
          </Form.Item>
          <Form.Item name="exam_ids" label="Exams (Subjects)" rules={[{ required: true, message: 'Please select at least one exam' }]}>
            <Select 
              mode="multiple" 
              placeholder={hallExams.length ? "Select exams" : "Select a hall first to view its exams"}
              disabled={hallExams.length === 0}
              options={hallExams.map(e => ({ 
                label: `${e.subject_name} (${e.exam_date} ${e.start_time} - ${e.end_time})`, 
                value: e.id 
              }))} 
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default InvigilatorManagement;
