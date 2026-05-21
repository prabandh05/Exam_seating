import React, { useEffect, useState } from 'react';
import { Table, Tag } from 'antd';
import { adminAPI } from '../../api';

const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    adminAPI.getAuditLogs({ page, page_size: 50 }).then(res => {
      setLogs(res.data.logs);
      setTotal(res.data.total);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [page]);

  const columns = [
    { title: 'Date', dataIndex: 'created_at', render: (v: string) => new Date(v).toLocaleString() },
    { title: 'User Role', dataIndex: 'user_role', render: (v: string) => <Tag>{v}</Tag> },
    { title: 'User ID', dataIndex: 'user_id' },
    { title: 'Action', dataIndex: 'action' },
    { title: 'Entity', dataIndex: 'entity_type' },
    { title: 'Entity ID', dataIndex: 'entity_id' },
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header"><h2>Audit Logs</h2></div>
      <Table dataSource={logs} columns={columns} rowKey="id" loading={loading}
             pagination={{ current: page, total, pageSize: 50, onChange: setPage }} />
    </div>
  );
};

export default AuditLogsPage;
