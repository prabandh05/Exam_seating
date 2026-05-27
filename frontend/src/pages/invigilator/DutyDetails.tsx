import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Table, Select, Button, message, Space, Tag, Descriptions, Popconfirm, Alert, Row, Col, Statistic } from 'antd';
import { LeftOutlined, CheckCircleOutlined, SaveOutlined } from '@ant-design/icons';
import { invigilatorAPI } from '../../api';

const DutyDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [seatings, setSeatings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [attendance, setAttendance] = useState<Record<number, string>>({});
  const [examInfo, setExamInfo] = useState<any>(null);
  const [hallNumber, setHallNumber] = useState('');
  const [completing, setCompleting] = useState(false);

  const fetchData = () => {
    setLoading(true);
    invigilatorAPI.getDutySeating(Number(id)).then(res => {
      setSeatings(res.data.seatings);
      setExamInfo(res.data.exam_info || null);
      setHallNumber(res.data.hall_number || '');
      const initial: Record<number, string> = {};
      res.data.seatings.forEach((s: any) => {
        initial[s.id] = s.attendance_status || 'present';
      });
      setAttendance(initial);
    }).catch(() => message.error('Failed to load seating')).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [id]);

  const handleSubmit = async () => {
    setLoading(true);
    const records = Object.entries(attendance).map(([seating_id, status]) => ({
      seating_id: Number(seating_id), status,
    }));
    try {
      await invigilatorAPI.markAttendance(Number(id), { attendance_records: records });
      message.success('Attendance submitted successfully');
    } catch {
      message.error('Failed to submit attendance');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    setCompleting(true);
    try {
      await invigilatorAPI.completeDuty(Number(id));
      message.success('Exam marked as completed');
      fetchData();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Failed to complete exam');
    } finally {
      setCompleting(false);
    }
  };

  const isCompleted = examInfo?.status === 'completed';

  const columns = [
    {
      title: 'Zone',
      dataIndex: 'zone',
      key: 'zone',
      sorter: (a: any, b: any) => a.zone.localeCompare(b.zone),
      render: (v: string) => (
        <Tag color="geekblue" style={{ fontWeight: 600, fontSize: 13 }}>{v}</Tag>
      ),
    },
    {
      title: 'Seat No.',
      dataIndex: 'seat_number',
      key: 'seat',
      sorter: (a: any, b: any) => {
        const parseRC = (s: string) => {
          const m = s.match(/R(\d+)C(\d+)/);
          return m ? [parseInt(m[1]), parseInt(m[2])] : [0, 0];
        };
        const [ar, ac] = parseRC(a.seat_number);
        const [br, bc] = parseRC(b.seat_number);
        return ar !== br ? ar - br : ac - bc;
      },
      render: (v: string) => <Tag color="blue" style={{ fontWeight: 600 }}>{v}</Tag>,
    },
    {
      title: 'Row',
      dataIndex: 'row_number',
      key: 'row',
      sorter: (a: any, b: any) => a.row_number - b.row_number,
    },
    {
      title: 'Column',
      dataIndex: 'column_number',
      key: 'col',
      sorter: (a: any, b: any) => a.column_number - b.column_number,
    },
    { title: 'Reg No', dataIndex: 'register_number', key: 'reg' },
    { title: 'Name', dataIndex: 'student_name', key: 'name' },
    { title: 'Department', dataIndex: 'department', key: 'dept' },
    {
      title: 'Attendance', key: 'attendance',
      render: (_: any, r: any) => (
        <Select
          style={{ width: 120 }}
          value={attendance[r.id] || 'present'}
          disabled={isCompleted}
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

  const presentCount = Object.values(attendance).filter(v => v === 'present').length;
  const absentCount = Object.values(attendance).filter(v => v === 'absent').length;
  const lateCount = Object.values(attendance).filter(v => v === 'late').length;

  return (
    <div className="fade-in-up">
      <div className="page-header">
        <Space>
          <Button icon={<LeftOutlined />} onClick={() => navigate('/invigilator')}>Back</Button>
          <h2>Duty Details</h2>
          {isCompleted && <Tag color="purple" style={{ fontSize: 14 }}>COMPLETED</Tag>}
        </Space>
        <Space>
          {!isCompleted && (
            <Button type="primary" icon={<SaveOutlined />} onClick={handleSubmit} loading={loading}>
              Submit Attendance
            </Button>
          )}
          {!isCompleted && (
            <Popconfirm
              title="Mark Exam as Completed?"
              description="This will finalize the exam. Make sure attendance is submitted first."
              onConfirm={handleComplete}
              okText="Yes, Complete"
              cancelText="Cancel"
            >
              <Button
                type="primary"
                danger
                icon={<CheckCircleOutlined />}
                loading={completing}
              >
                Mark Exam Completed
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      {/* Exam Info */}
      {examInfo && (
        <Card style={{ marginBottom: 16 }}>
          <Descriptions title="Exam Information" column={{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }}>
            <Descriptions.Item label="Subject">{examInfo.subject_name}</Descriptions.Item>
            <Descriptions.Item label="Date">{examInfo.exam_date}</Descriptions.Item>
            <Descriptions.Item label="Time">{examInfo.start_time} – {examInfo.end_time}</Descriptions.Item>
            <Descriptions.Item label="Hall">{hallNumber}</Descriptions.Item>
            <Descriptions.Item label="Status">
              <Tag color={examInfo.status === 'completed' ? 'purple' : 'blue'}>{examInfo.status?.toUpperCase()}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Total Students">{seatings.length}</Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {/* Attendance Summary */}
      {seatings.length > 0 && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col><Statistic title="Total" value={seatings.length} /></Col>
          <Col><Statistic title="Present" value={presentCount} valueStyle={{ color: '#10b981' }} /></Col>
          <Col><Statistic title="Absent" value={absentCount} valueStyle={{ color: '#ef4444' }} /></Col>
          <Col><Statistic title="Late" value={lateCount} valueStyle={{ color: '#f59e0b' }} /></Col>
          <Col>
            <Statistic
              title="Unmarked"
              value={seatings.length - Object.keys(attendance).length}
              valueStyle={{ color: '#8c8c8c' }}
            />
          </Col>
        </Row>
      )}

      {isCompleted && (
        <Alert
          message="This exam has been completed"
          description="Attendance has been finalized. No further changes can be made."
          type="success"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Card>
        <Table
          dataSource={seatings}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={seatings.length > 20 ? { pageSize: 20, showTotal: (t) => `Total ${t} students` } : false}
          scroll={{ x: true }}
        />
      </Card>
    </div>
  );
};

export default DutyDetails;
