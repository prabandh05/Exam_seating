import React, { useEffect, useState, useCallback } from 'react';
import {
  Card, Select, Button, Space, Table, message, Modal, Tag, Alert,
  Popconfirm, Tabs, Row, Col, Tooltip, Statistic, Badge, Empty
} from 'antd';
import {
  BookOutlined, LayoutOutlined, TableOutlined, DeleteOutlined,
  ExportOutlined, ReloadOutlined, UserAddOutlined
} from '@ant-design/icons';
import { adminAPI } from '../../api';

// ─── Types ───
interface SeatOccupant {
  id: number;
  exam_id: number;
  exam_name: string;
  student_id: number;
  student_name: string;
  register_number: string;
  department: string;
  is_locked: boolean;
}

interface LayoutData {
  hall: { id: number; hall_number: string; num_rows: number; num_columns: number; capacity: number };
  seating_map: Record<string, SeatOccupant>;
  unassigned_students: { id: number; name: string; register_number: string; department: string }[];
}

const STATUS_COLOR: Record<string, string> = {
  draft: '#faad14', published: '#1677ff', ongoing: '#52c41a',
  completed: '#722ed1', cancelled: '#ff4d4f'
};

// ─── Component ───
const SeatingArrangement: React.FC = () => {
  const [activeTab, setActiveTab] = useState('1');
  const [exams, setExams] = useState<any[]>([]);
  const [halls, setHalls] = useState<any[]>([]);

  // Tab 1: Auto-generate
  const [selectedExams, setSelectedExams] = useState<number[]>([]);
  const [selectedHalls, setSelectedHalls] = useState<number[]>([]);
  const [mode, setMode] = useState('mixed_subject');
  const [generating, setGenerating] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);

  // Tab 2: Manual editor
  const [manualExamId, setManualExamId] = useState<number | null>(null);
  const [manualHallId, setManualHallId] = useState<number | null>(null);
  const [layoutData, setLayoutData] = useState<LayoutData | null>(null);
  const [layoutLoading, setLayoutLoading] = useState(false);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedSeat, setSelectedSeat] = useState<{ row: number; col: number; seatNum: string } | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  // Tab 3: Current seating view
  const [viewExamId, setViewExamId] = useState<number | null>(null);
  const [viewSeatings, setViewSeatings] = useState<any[]>([]);
  const [viewLoading, setViewLoading] = useState(false);
  const [viewConflicts, setViewConflicts] = useState<any>(null);

  // ─── Fetch master data ───
  const fetchMasterData = useCallback(() => {
    adminAPI.getExams().then(r => setExams(r.data.exams)).catch(() => {});
    adminAPI.getHalls({ is_enabled: true }).then(r => setHalls(r.data.halls)).catch(() => {});
  }, []);

  useEffect(() => { fetchMasterData(); }, [fetchMasterData]);

  // ─── Tab 1: Auto-generate ───
  const handleGenerate = async () => {
    if (!selectedExams.length || !selectedHalls.length) {
      return message.error('Select at least one exam and one hall');
    }
    setGenerating(true);
    try {
      const res = await adminAPI.generateSeating({
        exam_ids: selectedExams, hall_ids: selectedHalls, mode, clear_existing: true,
      });
      if (res.data.success) {
        message.success(res.data.message);
        if (res.data.conflicts_detected?.length) {
          Modal.warning({ title: 'Warning', content: res.data.conflicts_detected.join('\n') });
        }
        setPreviewData(res.data);
        fetchMasterData();
      } else {
        message.error(res.data.message);
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleConfirmPreview = () => {
    setPreviewData(null);
    message.success('Seating arrangement saved successfully');
    setActiveTab('3'); // Switch to Current Seating view
  };

  const handleDiscardPreview = async () => {
    try {
      for (const examId of selectedExams) {
        await adminAPI.clearSeating(examId);
      }
      setPreviewData(null);
      message.success('Generated seating discarded');
      fetchMasterData();
    } catch {
      message.error('Failed to discard seating');
    }
  };

  // ─── Tab 2: Load hall layout ───
  const loadLayout = useCallback(async (examId: number, hallId: number) => {
    setLayoutLoading(true);
    setLayoutData(null);
    try {
      const res = await adminAPI.getHallLayout(hallId, examId);
      setLayoutData(res.data);
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Failed to load hall layout');
    } finally {
      setLayoutLoading(false);
    }
  }, []);

  useEffect(() => {
    if (manualExamId && manualHallId) {
      loadLayout(manualExamId, manualHallId);
    } else {
      setLayoutData(null);
    }
  }, [manualExamId, manualHallId, loadLayout]);

  const currentExam = exams.find(e => e.id === manualExamId);
  const isEditable = currentExam?.status === 'draft' && !currentExam?.seating_locked;

  const handleSeatClick = (row: number, col: number, seatNum: string, occupant?: SeatOccupant) => {
    if (!isEditable) {
      return message.warning('Seating is locked or exam is not in draft status. Cannot edit.');
    }
    if (occupant) {
      if (occupant.exam_id !== manualExamId) {
        return message.info('This seat belongs to an overlapping exam and cannot be modified here.');
      }
      Modal.confirm({
        title: 'Remove Student?',
        content: `Unassign ${occupant.student_name} (${occupant.register_number}) from seat ${seatNum}?`,
        okText: 'Remove', okType: 'danger',
        onOk: async () => {
          try {
            await adminAPI.manualRemoveSeat(occupant.id);
            message.success('Student removed from seat');
            loadLayout(manualExamId!, manualHallId!);
          } catch (e: any) {
            message.error(e.response?.data?.detail || 'Failed to remove');
          }
        }
      });
    } else {
      setSelectedSeat({ row, col, seatNum });
      setSelectedStudentId(null);
      setAssignModalOpen(true);
    }
  };

  const handleAssignSeat = async () => {
    if (!selectedStudentId || !selectedSeat) return;
    setSaving(true);
    try {
      await adminAPI.manualAssignSeat({
        exam_id: manualExamId,
        hall_id: manualHallId,
        student_id: selectedStudentId,
        row_number: selectedSeat.row,
        column_number: selectedSeat.col,
      });
      message.success(`Student assigned to seat ${selectedSeat.seatNum}`);
      setAssignModalOpen(false);
      loadLayout(manualExamId!, manualHallId!);
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Failed to assign student');
    } finally {
      setSaving(false);
    }
  };

  // ─── Tab 3: View current seating ───
  const loadViewSeating = async (examId: number) => {
    setViewExamId(examId);
    setViewLoading(true);
    setViewSeatings([]);
    setViewConflicts(null);
    try {
      const [seatRes, confRes] = await Promise.all([
        adminAPI.getSeating(examId),
        adminAPI.checkConflicts(examId),
      ]);
      setViewSeatings(seatRes.data.seatings);
      setViewConflicts(confRes.data);
    } catch {
      message.error('Failed to load seating data');
    } finally {
      setViewLoading(false);
    }
  };

  const handleClearSeating = async (examId: number) => {
    try {
      await adminAPI.clearSeating(examId);
      message.success('Seating cleared');
      setViewSeatings([]);
      setViewConflicts(null);
      fetchMasterData();
    } catch { message.error('Failed to clear seating'); }
  };

  const handleExportExcel = async (examId: number) => {
    try {
      const res = await adminAPI.exportSeatingExcel(examId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `seating_exam_${examId}.xlsx`;
      document.body.appendChild(a); a.click(); a.remove();
    } catch { message.error('Export failed'); }
  };

  // ─── Seat Grid rendering ───
  const renderSeatGrid = () => {
    if (!layoutData) return null;
    const { hall, seating_map } = layoutData;
    const totalSeats = hall.num_rows * hall.num_columns;
    const occupied = Object.values(seating_map).filter(o => o.exam_id === manualExamId).length;

    return (
      <div>
        {/* Stats bar */}
        <Row gutter={16} style={{ marginBottom: 20 }}>
          <Col><Statistic title="Total Seats" value={totalSeats} /></Col>
          <Col><Statistic title="This Exam" value={occupied} valueStyle={{ color: '#1677ff' }} /></Col>
          <Col><Statistic title="Available" value={totalSeats - Object.keys(seating_map).length} valueStyle={{ color: '#52c41a' }} /></Col>
          <Col><Statistic title="Other Exams" value={Object.keys(seating_map).length - occupied} valueStyle={{ color: '#8c8c8c' }} /></Col>
        </Row>

        {!isEditable && (
          <Alert message="Read-only mode — Exam is not in draft status or seating is locked." type="warning" showIcon style={{ marginBottom: 16 }} />
        )}

        {/* Legend */}
        <Space style={{ marginBottom: 16 }} wrap>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 20, height: 20, background: '#f6ffed', border: '2px solid #b7eb8f', borderRadius: 4, display: 'inline-block' }} />
            <span style={{ fontSize: 12 }}>Empty</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 20, height: 20, background: '#e6f7ff', border: '2px solid #91caff', borderRadius: 4, display: 'inline-block' }} />
            <span style={{ fontSize: 12 }}>This exam</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 20, height: 20, background: '#f5f5f5', border: '2px solid #d9d9d9', borderRadius: 4, display: 'inline-block' }} />
            <span style={{ fontSize: 12 }}>Overlapping exam</span>
          </span>
        </Space>

        {/* Blackboard */}
        <div style={{ width: '80%', height: 28, background: '#262626', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 4, margin: '0 auto 32px', fontSize: 12, letterSpacing: 2 }}>
          FRONT / BLACKBOARD
        </div>

        {/* Grid */}
        <div style={{ overflowX: 'auto' }}>
          {Array.from({ length: hall.num_rows }, (_, ri) => {
            const row = ri + 1;
            return (
              <div key={row} style={{ display: 'flex', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ width: 50, fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600, flexShrink: 0 }}>Row {row}</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 0 }}>
                  {Array.from({ length: hall.num_columns }, (_, ci) => {
                    const col = ci + 1;
                    const seatNum = `R${row}C${col}`;
                    const occupant = seating_map[seatNum];
                    const isThisExam = occupant?.exam_id === manualExamId;
                    const isOtherExam = occupant && !isThisExam;
                    const benchEnd = col % 2 === 0 && col !== hall.num_columns;

                    let bg = '#f6ffed', border = '#b7eb8f', color = '#389e0d';
                    let cursor = isEditable ? 'pointer' : 'default';
                    if (isThisExam) { bg = '#e6f7ff'; border = '#91caff'; color = '#0958d9'; }
                    if (isOtherExam) { bg = '#f5f5f5'; border = '#d9d9d9'; color = '#bfbfbf'; cursor = 'not-allowed'; }

                    const tip = isOtherExam
                      ? `${seatNum}: ${occupant.student_name} — ${occupant.exam_name}`
                      : isThisExam
                        ? `${seatNum}: ${occupant.student_name} (${occupant.register_number}) — Click to remove`
                        : `${seatNum}: Empty — Click to assign`;

                    return (
                      <React.Fragment key={col}>
                        <Tooltip title={tip} placement="top">
                          <div
                            onClick={() => handleSeatClick(row, col, seatNum, occupant)}
                            style={{
                              width: 52, height: 52, background: bg, border: `2px solid ${border}`,
                              color, borderRadius: 6, display: 'flex', flexDirection: 'column',
                              alignItems: 'center', justifyContent: 'center', cursor,
                              fontSize: 10, fontWeight: 600, userSelect: 'none',
                              transition: 'all 0.15s', margin: 3,
                            }}
                          >
                            <div>{seatNum}</div>
                            {isThisExam && (
                              <div style={{ fontSize: 9, maxWidth: 46, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', opacity: 0.8 }}>
                                {occupant.student_name.split(' ')[0]}
                              </div>
                            )}
                          </div>
                        </Tooltip>
                        {/* Bench aisle gap after every 2 columns */}
                        {benchEnd && <div style={{ width: 18, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#d9d9d9', fontSize: 16 }}>|</div>}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // ─── View columns ───
  const viewColumns = [
    { title: 'Hall', dataIndex: 'hall_number', key: 'hall', render: (v: string) => <strong>{v}</strong> },
    { title: 'Seat', dataIndex: 'seat_number', key: 'seat', render: (v: string) => <Tag color="blue">{v}</Tag> },
    { title: 'Register No', dataIndex: 'register_number', key: 'reg' },
    { title: 'Student Name', dataIndex: 'student_name', key: 'name' },
    { title: 'Department', dataIndex: 'department', key: 'dept' },
    { title: 'Subject', dataIndex: 'subject_name', key: 'sub' },
    { title: 'Row', dataIndex: 'row_number', key: 'row' },
    { title: 'Col', dataIndex: 'column_number', key: 'col' },
  ];

  return (
    <div className="fade-in-up" style={{ padding: '0 8px' }}>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Seating Arrangement</h2>
        <span style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
          Auto-generate, manually edit, or view saved seating for any exam.
        </span>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        style={{ background: 'var(--bg-card)', padding: '0 24px 24px', borderRadius: 12, boxShadow: 'var(--shadow)' }}
        items={[
          // ═══ TAB 1: AUTO-GENERATE ═══
          {
            key: '1',
            label: <span><LayoutOutlined /> Auto-Generate</span>,
            children: (
              <Space direction="vertical" style={{ width: '100%', paddingTop: 16 }} size="large">
                <Card style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8 }}>
                  <Space wrap size="large">
                    <div>
                      <div style={{ fontWeight: 500, marginBottom: 6 }}>Draft Exams</div>
                      <Select
                        mode="multiple" placeholder="Select exams to seat" style={{ minWidth: 300 }}
                        value={selectedExams} onChange={setSelectedExams}
                        options={exams.filter(e => e.status === 'draft').map(e => ({
                          label: `${e.subject_name} (${e.department} Sem ${e.semester})`, value: e.id
                        }))}
                      />
                    </div>
                    <div>
                      <div style={{ fontWeight: 500, marginBottom: 6 }}>Halls</div>
                      <Select
                        mode="multiple" placeholder="Select halls" style={{ minWidth: 220 }}
                        value={selectedHalls} onChange={setSelectedHalls}
                        options={halls.map(h => ({ label: `${h.hall_number} (Cap: ${h.capacity})`, value: h.id }))}
                      />
                    </div>
                    <div>
                      <div style={{ fontWeight: 500, marginBottom: 6 }}>Mode</div>
                      <Select value={mode} onChange={setMode} style={{ width: 230 }}
                        options={[
                          { label: 'Mixed Subject (Anti-Cheat)', value: 'mixed_subject' },
                          { label: 'Same Subject', value: 'same_subject' },
                          { label: 'Department Wise', value: 'department_wise' },
                          { label: 'Random Shuffle', value: 'random' },
                          { label: 'Alternate Seating (skip 1 seat)', value: 'alternate_seating' },
                          { label: 'Skip Bench (skip 1 bench)', value: 'skip_bench' },
                        ]}
                      />
                    </div>
                    <div style={{ alignSelf: 'flex-end' }}>
                      <Button type="primary" size="large" loading={generating} onClick={handleGenerate}>
                        Generate Seating Plan
                      </Button>
                    </div>
                  </Space>
                </Card>
                {previewData ? (
                  <Card title="Generated Seating Preview" style={{ borderRadius: 8, border: '1px solid var(--primary)' }}
                        extra={
                          <Space>
                            <Button danger onClick={handleDiscardPreview}>Discard</Button>
                            <Button type="primary" onClick={handleConfirmPreview}>Confirm & Save</Button>
                          </Space>
                        }>
                    <Alert message="Review the generated seating below. Click Confirm to finalize or Discard to try again." type="info" showIcon style={{ marginBottom: 16 }} />
                    <Table
                      dataSource={previewData.preview_seatings || []}
                      rowKey={(r: any) => `${r.exam_id}-${r.seat_number}`}
                      columns={viewColumns}
                      pagination={{ pageSize: 10 }}
                      scroll={{ x: true }}
                    />
                  </Card>
                ) : (
                  <Alert
                    message="After generating, review the preview here before confirming, or use the Interactive Editor to make manual adjustments."
                    type="info" showIcon
                  />
                )}
              </Space>
            ),
          },

          // ═══ TAB 2: INTERACTIVE MANUAL EDITOR ═══
          {
            key: '2',
            label: <span><BookOutlined /> Interactive Editor</span>,
            children: (
              <Row gutter={[20, 20]} style={{ paddingTop: 16 }}>
                {/* Controls */}
                <Col xs={24} md={7}>
                  <Card title="Select Exam & Hall" style={{ borderRadius: 8 }}>
                    <Space direction="vertical" style={{ width: '100%' }} size="middle">
                      <div>
                        <div style={{ fontWeight: 500, marginBottom: 6 }}>Exam</div>
                        <Select
                          showSearch placeholder="Select exam" style={{ width: '100%' }}
                          optionFilterProp="label" value={manualExamId}
                          onChange={v => { setManualExamId(v); setManualHallId(null); setLayoutData(null); }}
                          options={exams.map(e => ({
                            label: `${e.subject_name} (${e.department})`,
                            value: e.id,
                          }))}
                        />
                      </div>
                      <div>
                        <div style={{ fontWeight: 500, marginBottom: 6 }}>Hall</div>
                        <Select
                          placeholder="Select hall" style={{ width: '100%' }}
                          disabled={!manualExamId} value={manualHallId} onChange={setManualHallId}
                          options={halls.map(h => ({ label: `Hall ${h.hall_number} (Cap: ${h.capacity})`, value: h.id }))}
                        />
                      </div>
                      {manualExamId && (
                        <div style={{ padding: '10px 12px', background: 'var(--bg-elevated)', borderRadius: 6, border: '1px solid var(--border)' }}>
                          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Exam Status</div>
                          <Tag color={STATUS_COLOR[currentExam?.status] || 'default'} style={{ marginTop: 4 }}>
                            {currentExam?.status?.toUpperCase()}
                          </Tag>
                          {!isEditable && (
                            <div style={{ fontSize: 11, color: '#ff4d4f', marginTop: 6 }}>
                              ⚠ Seating is locked or exam is not in draft. View only.
                            </div>
                          )}
                        </div>
                      )}
                      {layoutData && (
                        <Button icon={<ReloadOutlined />} onClick={() => loadLayout(manualExamId!, manualHallId!)} block>
                          Refresh Layout
                        </Button>
                      )}
                    </Space>
                  </Card>
                </Col>

                {/* Grid */}
                <Col xs={24} md={17}>
                  <Card
                    title={layoutData ? `Hall ${layoutData.hall.hall_number} — Seat Map` : 'Seat Map'}
                    style={{ borderRadius: 8, minHeight: 400 }}
                    loading={layoutLoading}
                  >
                    {layoutData ? renderSeatGrid() : (
                      <Empty description="Select an exam and hall to load the interactive seating map" style={{ padding: '60px 0' }} />
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },

          // ═══ TAB 3: CURRENT SEATING VIEW ═══
          {
            key: '3',
            label: <span><TableOutlined /> Current Seating</span>,
            children: (
              <Space direction="vertical" style={{ width: '100%', paddingTop: 16 }} size="large">
                <Card title="Select Exam to View Seating" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8 }}>
                  <Table 
                    dataSource={exams.filter(e => e.total_students_assigned > 0 || e.status === 'published' || e.status === 'ongoing' || e.status === 'completed')}
                    rowKey="id"
                    pagination={{ pageSize: 5 }}
                    onRow={(record) => ({
                      onClick: () => loadViewSeating(record.id),
                      style: { cursor: 'pointer', background: viewExamId === record.id ? 'var(--bg-active)' : undefined }
                    })}
                    columns={[
                      { title: 'Subject', dataIndex: 'subject_name', key: 'sub' },
                      { title: 'Department', dataIndex: 'department', key: 'dep' },
                      { title: 'Date', dataIndex: 'exam_date', key: 'date' },
                      { title: 'Status', dataIndex: 'status', key: 'status', render: (v: any) => <Tag color={STATUS_COLOR[v] || 'default'}>{v?.toUpperCase()}</Tag> },
                      { title: 'Students Seated', dataIndex: 'total_students_assigned', key: 'count', render: (v: any) => <Badge count={v} showZero color="#1677ff" /> },
                      { title: 'Action', key: 'action', render: (_: any, r: any) => <Button type={viewExamId === r.id ? 'primary' : 'default'} onClick={(e) => { e.stopPropagation(); loadViewSeating(r.id); }}>View Seating</Button>}
                    ]}
                  />
                  {viewExamId && (
                    <div style={{ marginTop: 16, textAlign: 'right' }}>
                      <Button icon={<ReloadOutlined />} onClick={() => loadViewSeating(viewExamId)}>
                        Refresh Data
                      </Button>
                    </div>
                  )}
                </Card>

                {viewConflicts?.has_conflicts && (
                  <Alert
                    message={`${viewConflicts.total_conflicts} Conflict(s) Detected`}
                    description={
                      <ul style={{ margin: 0, paddingLeft: 20 }}>
                        {viewConflicts.conflicts.map((c: string, i: number) => <li key={i}>{c}</li>)}
                      </ul>
                    }
                    type="error" showIcon
                  />
                )}

                {viewExamId && (
                  <Card
                    title={
                      <Space>
                        <span style={{ fontWeight: 600 }}>
                          {exams.find(e => e.id === viewExamId)?.subject_name} — Seating Plan
                        </span>
                        <Badge count={viewSeatings.length} style={{ background: '#1677ff' }} showZero />
                      </Space>
                    }
                    extra={
                      <Space>
                        <Button
                          icon={<ExportOutlined />}
                          onClick={() => handleExportExcel(viewExamId)}
                          disabled={!viewSeatings.length}
                        >
                          Export Excel
                        </Button>
                        {exams.find(e => e.id === viewExamId)?.status === 'draft' && (
                          <Popconfirm
                            title="Clear all seating for this exam?"
                            description="This cannot be undone."
                            onConfirm={() => handleClearSeating(viewExamId)}
                          >
                            <Button danger icon={<DeleteOutlined />}>Clear Seating</Button>
                          </Popconfirm>
                        )}
                      </Space>
                    }
                    style={{ borderRadius: 8 }}
                  >
                    {viewSeatings.length === 0 && !viewLoading ? (
                      <Empty description="No seating arrangement found for this exam. Generate or manually assign seats first." />
                    ) : (
                      <Table
                        dataSource={viewSeatings}
                        rowKey="id"
                        loading={viewLoading}
                        columns={viewColumns}
                        pagination={{ pageSize: 15, showTotal: (t) => `Total ${t} students seated` }}
                        scroll={{ x: true }}
                      />
                    )}
                  </Card>
                )}

                {!viewExamId && (
                  <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description="Select an exam above to view its current seating arrangement (whether auto-generated or manually assigned)."
                    style={{ padding: '40px 0' }}
                  />
                )}
              </Space>
            ),
          },
        ]}
      />

      {/* Assign Student Modal */}
      <Modal
        title={`Assign Student → Seat ${selectedSeat?.seatNum}`}
        open={assignModalOpen}
        onCancel={() => { setAssignModalOpen(false); setSelectedStudentId(null); }}
        onOk={handleAssignSeat}
        okText="Assign Seat"
        okButtonProps={{ disabled: !selectedStudentId, loading: saving }}
        width={480}
      >
        {layoutData?.unassigned_students.length ? (
          <>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>
              Choose an eligible unassigned student for this exam:
            </p>
            <Select
              showSearch optionFilterProp="label" placeholder="Search by name or register number"
              style={{ width: '100%' }} value={selectedStudentId} onChange={setSelectedStudentId}
              options={layoutData.unassigned_students.map(s => ({
                value: s.id,
                label: `${s.name} (${s.register_number}) — ${s.department}`,
              }))}
            />
          </>
        ) : (
          <Alert
            message="No unassigned students"
            description="All eligible students in this department & semester are already seated."
            type="warning" showIcon
          />
        )}
      </Modal>
    </div>
  );
};

export default SeatingArrangement;
