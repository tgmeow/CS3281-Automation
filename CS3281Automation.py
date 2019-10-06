from datetime import datetime
import git
import os
import pytz
"""
Rough flow:
User goes 'into' an assignment
Checks status (exists, not found)
Has actions depending on status (commit all grade.md) (clone from user lists in txt depending on group) 
"""

# TODO put hard coded things in config file, put groups in a single table rather than
#  individual files for single read to mem.
def main():
    input_command = ''
    assignments_dir = os.path.dirname(os.getcwd())
    print(assignments_dir)
    assignment = Assignment(assignments_dir)

    # repo = git.Repo(os.path.join(assignments_dir, 'Automation', 'test-gitpython'))
    # local_commit = repo.commit()
    # remote = git.remote.Remote(repo, 'origin')
    # remote_fetch = remote.fetch()
    # remote_commit_latest = remote_fetch[0].commit
    # if local_commit.hexsha != remote_commit_latest.hexsha:
    #     print('Repo %s has new commits in remote!' % 'test')

    # TODO(HIGH) Add flush=True to most/all of the looped print statements.
    while True:
        input_command = input('Command: (help, q, activate, push_grading, status, print_grades, check_commits, check_commit_date)\n')
        ic_arr = input_command.split(' ')
        # TODO(LOW) use map
        if ic_arr[0] == 'q':
            break
        elif ic_arr[0] == 'help':
            print('TODO LOLOL') # TODO(MED) add help
        elif ic_arr[0] == 'activate':
            if len(ic_arr) == 1:
                assignment.choose_assignment()
            else:
                if assignment.is_valid_int(ic_arr[1]):
                    assignment.activate_assignment(int(ic_arr[1]))
                else:
                    print("Error: second parameter is not a number.")
        elif ic_arr[0] == 'push_grading':
            # TODO(MED) Ask for CONFIRMATION!!!
            assignment.add_commit_push_grade_md('Add Grade.md')
        elif ic_arr[0] == 'status':
            if assignment.activated:
                print('Activated on assignment %d' % assignment.assignment_number)
                # TODO(LOW) more detail on status of repos
        elif ic_arr[0] == 'print_grades':
            assignment.print_grades()
        elif ic_arr[0] == 'check_commits':
            assignment.check_for_new_commits()
        elif ic_arr[0] == 'check_commit_date':
            if len(ic_arr) == 1:
                assignment.check_commit_date(0)
            else:
                if assignment.is_valid_int(ic_arr[1]):
                    assignment.check_commit_date(int(ic_arr[1]))
                else:
                    print("Error: second parameter is not a number.")

        else:
            print('Unknown command: %s' % ic_arr[0])


class Assignment:
    def __init__(self, assignments_path_root):
        """
        :param assignments_path_root: Root directory containing folders of all assignment numbers.
        """
        self.assignments_path_root = assignments_path_root
        self.active_assignment_path = ''
        self.assignment_number = -1
        self.activated = False
        self.assignment_folder_template = 'assignment%d'

    def choose_assignment(self):
        """
        Prompts user to enter an assignment number and then activates that assignment.
        """
        number = self._input_int('Assignment number: ', 'Not a valid assignment number!')
        print('Using assignment %d' % number)
        self.activate_assignment(number)

    def activate_assignment(self, assignment_number):
        self.assignment_number = assignment_number
        self.active_assignment_path = self.check_exists()
        if self.active_assignment_path != '':
            self.activated = True
            print('Assignment %d activated.' % self.assignment_number)
        else:
            self.activated = False
            ans = input('Would you like to clone assignment %d from GitHub? (y/n)' % self.assignment_number)
            if ans.lower() == 'y':
                self.activated = True
                self.clone_new_assignment()

    def add_commit_push_grade_md(self, message):
        if not self._check_activated():
            return
        repos = os.listdir(self.active_assignment_path)
        for student in repos:
            repo_path = os.path.join(self.active_assignment_path, student)
            print(repo_path, flush=True)
            repo = git.repo.Repo(repo_path)
            # TODO(LOW) change assert to something else
            assert not repo.bare
            print('Untracked files: %s' % repo.untracked_files)
            print('Adding grade.md')
            # TODO(LOW) change assert to something else
            assert 'grade.md' in repo.untracked_files
            repo.index.add(['grade.md'])
            print('Creating commit')
            repo.index.commit(message)
            print('Pushing to origin master', flush=True)
            repo.remote('origin').push('master')

    def check_exists(self):
        if os.path.isdir(self.assignments_path_root):
            path = os.path.join(self.assignments_path_root,
                                self.assignment_folder_template % self.assignment_number)
            print(path)
            if os.path.isdir(path):
                print('Located assignment %d.' % self.assignment_number)
                return path
            else:
                print('Assignment %d does not exist.' % self.assignment_number)
                return ''
        else:
            raise SystemError('Unable to locate assignments path root %s' % self.assignments_path_root)

    def clone_new_assignment(self):
        if not self._check_activated():
            return
        print('Cloning assignment number %d' % self.assignment_number)
        group = self._input_int('Grading group: ', 'Not a valid group!')
        print('Cloning group %d' % group)
        group_file_path = os.path.join(self.assignments_path_root, 'group%d.txt' % group)
        github_ids = []
        if os.path.isfile(group_file_path):
            with open(group_file_path, 'r') as fin:
                for line in fin.readlines():
                    github_ids.append(line.rstrip())
        # TODO(MED) add confirm dialogue with these github IDs before continuing.

        if os.path.isdir(self.assignments_path_root):
            assignment_path = os.path.join(self.assignments_path_root,
                                self.assignment_folder_template % self.assignment_number)
            # Create assignment dir if not there.
            if not os.path.isdir(assignment_path):
                os.mkdir(assignment_path)
            # Download all github ids.
            for github_id in github_ids:
                if github_id == "" or github_id == " ":
                    continue
                print('Cloning user: %s' % github_id, flush=True)
                # TODO(LOW) ensure repo_path does not exist (shouldn't happen if creating new assignment dir) else ask
                repo_path = os.path.join(assignment_path, 'assignment-%d-%s'%(self.assignment_number,github_id))
                repo = git.repo.Repo.clone_from('https://github.com/cs3281/assignment-%d-%s.git'%(self.assignment_number, github_id),
                                                repo_path)
        return

    def check_for_new_commits(self):
        if not self._check_activated():
            return
        print('Checking for updates in assignment %d' % self.assignment_number)
        # Assume assignment dir is correct and exists
        assignment_path = os.path.join(self.assignments_path_root,
                                       self.assignment_folder_template % self.assignment_number)
        for folder in os.listdir(assignment_path):
            git_dir = os.path.join(assignment_path, folder)
            if not os.path.isdir(git_dir):
                print("Unexpected file : %s" % folder)
            else:
                print(folder)
                repo = git.Repo(git_dir)
                local_commit = repo.commit()
                remote = git.remote.Remote(repo, 'origin')
                remote_commit = remote.fetch()[0].commit
                if local_commit.hexsha != remote_commit.hexsha:
                    print('Repo %s has new commits in remote!' % folder)
        return

    def check_commit_date(self, num_parents):
        """
        Prints commit date. NOTE: It is possible to rewrite commit dates of git commits.
        TODO check if assignment is overdue
        :return:
        """
        if not self._check_activated():
            return
        print('Checking due dates in assignment %d' % self.assignment_number)
        # Assume assignment dir is correct and exists
        assignment_path = os.path.join(self.assignments_path_root,
                                       self.assignment_folder_template % self.assignment_number)
        for folder in os.listdir(assignment_path):
            git_dir = os.path.join(assignment_path, folder)
            if not os.path.isdir(git_dir):
                print("Unexpected file : %s" % folder)
            else:
                print(folder)
                repo = git.Repo(git_dir)
                local_commit = repo.commit('master' + (num_parents * '^'))
                commit_datetime = local_commit.committed_datetime
                tz = pytz.timezone('America/Chicago')
                dt = commit_datetime.astimezone(tz)
                print(dt.strftime('%Y-%m-%d %H:%M:%S'), flush=True)


    def print_grades(self):
        if not self._check_activated():
            return
        print('Grades for assignment %d:' % self.assignment_number)
        repos = os.listdir(self.active_assignment_path)
        for student in repos:
            repo = os.path.join(self.active_assignment_path, student)
            grade_file = os.path.join(repo, 'grade.md')
            print('** Student %s **' % student)
            if os.path.isfile(grade_file):
                with open(grade_file, 'r') as fin:
                    print('%s\n' % fin.read())
            else:
                print('Missing grade.md!')

    def _check_activated(self):
        if not self.activated:
            print('Error: assignment has not been chosen.')
        return self.activated

    def _input_int(self, prompt, error):
        while True:
            input_string = input(prompt)
            if self.is_valid_int(input_string):
                return int(input_string)
            else:
                print(error)

    def is_valid_int(self, int_string):
        try:
            int(int_string)
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    main()
