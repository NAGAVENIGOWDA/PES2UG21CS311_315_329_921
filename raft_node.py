import requests
import json
import threading
import random
import time

class RaftNode:
    def __init__(self, node_id, peers, flask_url):
        self.node_id = node_id
        self.peers = peers
        self.flask_url = flask_url
        self.state = 'follower'
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {peer: 0 for peer in peers}
        self.match_index = {peer: 0 for peer in peers}
        self.election_timer = None
        self.heartbeat_timer = None
 
    def start(self):
        self.start_election_timer()

    def start_election_timer(self):
        self.cancel_election_timer()
        self.election_timer = threading.Timer(random.uniform(5, 10), self.start_election)
        self.election_timer.start()

    def start_heartbeat_timer(self):
        self.cancel_heartbeat_timer()
        self.heartbeat_timer = threading.Timer(1, self.send_heartbeat)
        self.heartbeat_timer.start()

    def cancel_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()

    def cancel_heartbeat_timer(self):
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()

    def send_heartbeat(self):
        if self.state == 'leader':
            for peer in self.peers:
                self.send_append_entries(peer)
            self.start_heartbeat_timer()
            print(f"Node {self.node_id} (Leader) - State: {self.state}, Leader ID: {self.node_id}")
        elif self.state == 'follower':
            # Reset the heartbeat timer for followers
            self.start_heartbeat_timer()
            print(f"Node {self.node_id} (Follower) - State: {self.state}, Leader ID: {self.voted_for}")
        else:
            print(f"Node {self.node_id} - State: {self.state}, Leader ID: {self.voted_for}")

    def start_election(self):
        if self.state == 'follower':
            self.state = 'candidate'
            self.current_term += 1
            self.voted_for = self.node_id
            self.start_election_timer()
            self.request_votes()
        print(f"Node {self.node_id} - State: {self.state}")

    def request_votes(self):
        votes_received = 1  # Vote for self
        total_peers = len(self.peers) + 1  # Including self
        print(f"Node {self.node_id} - Requesting votes...")
        for peer in self.peers:
            # Send RequestVote RPC to all other nodes
            vote_granted = self.send_request_vote(peer)
            if vote_granted:
                votes_received += 1
                print(f"Node {self.node_id} - Received vote from Node {peer}")
            else:
                print(f"Node {self.node_id} - Did not receive vote from Node {peer}")
            if votes_received > total_peers / 2:
                self.become_leader()
                return
        print(f"Node {self.node_id} - Did not receive enough votes to become leader")

    def send_request_vote(self, peer):
        payload = {
            'term': self.current_term,
            'candidate_id': self.node_id,
            'last_log_index': len(self.log) - 1 if self.log else 0,
            'last_log_term': self.log[-1]['term'] if self.log else 0
        }
        print(f"Node {self.node_id} - Sending vote request to Node {peer}")
        response = requests.post(f"{self.flask_url}/request_vote", json=payload)
        try:
            response_data = response.json()
            vote_granted = response_data.get('vote_granted', False)
        except json.decoder.JSONDecodeError:
            vote_granted = False
        return vote_granted

    def receive_request_vote(self, term, candidate_id, last_log_index, last_log_term):
        if term < self.current_term:
            return False
        if term > self.current_term or (self.voted_for is None or self.voted_for == candidate_id):
            self.current_term = term
            self.voted_for = candidate_id
            self.start_election_timer()
            return True
        return False

    def become_leader(self):
        self.state = 'leader'
        self.voted_for = None
        self.start_heartbeat_timer()
        print(f"Node {self.node_id} - State: {self.state}, Leader ID: {self.node_id}")

    def send_append_entries(self, peer):
        payload = {
            'term': self.current_term,
            'leader_id': self.node_id,
            'prev_log_index': self.next_index[peer] - 1,
            'prev_log_term': self.log[self.next_index[peer] - 1]['term'] if self.next_index[peer] > 0 else 0,
            'entries': self.log[self.next_index[peer]:],
            'leader_commit': self.commit_index
        }
        response = requests.post(f"{self.flask_url}/append_entries", json=payload)
        print(f"Node {self.node_id} (Leader) - Sent heartbeat to Node {peer}")



    def update_task(self, task_id, updated_data):
        payload = {
            'title': updated_data['title'],
            'description': updated_data['description'],
            'status': updated_data['status']
        }
        response = requests.patch(f"{self.flask_url}/tasks/{task_id}", json=payload)
        print(f"Node {self.node_id} - Task updated: {response.text}")

    def delete_task(self, task_id):
        response = requests.delete(f"{self.flask_url}/tasks/{task_id}")
        print(f"Node {self.node_id} - Task deleted: {response.text}")

# Example usage:
if __name__ == "__main__":
    node1 = RaftNode(node_id=1, peers=[2, 3], flask_url="http://127.0.0.1:5000")
    node2 = RaftNode(node_id=2, peers=[1, 3], flask_url="http://127.0.0.1:5000")
    node3 = RaftNode(node_id=3, peers=[1, 2], flask_url="http://127.0.0.1:5000")

    node1.start()
    node2.start()
    node3.start()
