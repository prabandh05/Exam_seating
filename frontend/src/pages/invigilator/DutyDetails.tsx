import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Table, Select, Button, message, Space, Tag } from 'antd';
import { LeftOutlined } from '@ant-design/icons';
import { invigilatorAPI } from '../../api';

const DutyDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [seatings, setSeatings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [attendance, setAttendance] = useState<Record<number, string>>({});

  useEffect(() => {
    invigilatorAPI.getDutySeating(Number(id)).then(res => {
      setSeatings(res.data.seatings);
      const initial: Record<number, string> = {};
      res.data.seatings.forEach((s: any) => {
        if (s.attendance_status) initial[s.id] = s.attendance_status;
      });
      setAttendance(initial);
    }).catch(() => message.error('Failed to load seating')).finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async () => {
    setLoading(true);
    const records = Object.entries(attendance).map(([seating_id, status]) => ({
      seating_id: Number(seating_id), status,
    }));
    try {
      await invigilatorAPI.markAttendance(Number(id), { attendance_records: records });
      message.success('Attendance submitted');
    } catch {
      message.error('Failed to submit attendance');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: 'Seat', dataIndex: 'seat_number', key: 'seat' },
    { title: 'Reg No', dataIndex: 'register_number', key: 'reg' },
    { title: 'Name', dataIndex: 'student_name', key: 'name' },
    { title: 'Department', dataIndex: 'department', key: 'dept' },
    {
      title: 'Attendance', key: 'attendance',
      render: (_: any, r: any) => (
        <Select
          style={{ width: 120 }}
          value={attendance[r.id] || 'present'}
          onChange={(v) => setAttendance({ ...attendance, [r.id]: v })}
          options={[
            { label: <span style={{ color: '#10b981' }}>Present</span>, value: 'present' },
            { label: <span style={{ color: '#ef4444' }}>Absent</span>, value: 'absent' },
            { label: <span style={{ color: '#f59e0b' }}>Late</span>, value: 'late' },
          ]}
        />
      ),
    },
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <Space>
          <Button icon={<LeftOutlined />} onClick={() => navigate('/invigilator')}>Back</Button>
          <h2>Duty Details</h2>
        </Space>
        <Button type="primary" onClick={handleSubmit} loading={loading}>Submit Attendance</Button>
      </div>
      <Card>
        <Table dataSource={seatings} columns={columns} rowKey="id" loading={loading} pagination={false} />
      </Card>
    </div>
  );
};

export default DutyDetails;
