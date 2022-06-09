import docx2txt
import re
import os


class ExtractText:
    def __init__(self, filename):
        """Intialization function

        Args:
            filename (str): The filename for the file from which text is to be extracted
            folder (str): In the case of a folder needing processing, the foldername is specified here
        """
        # Regular expressions for extracting parts of the text
        # Extract the job title from the text
        self.job_title = re.compile(
            '^(title of position: \w+)|^(job title: \w+)', re.I)

        # Extract the experience from the text

        self.experience_regex = re.compile(
            r'\d+\syears?', re.IGNORECASE)

        self.month_experience_regex = re.compile('\d+\smonths?', re.IGNORECASE)

        self.word_month_xp_regex = re.compile(r'\w+\smonths?', re.IGNORECASE)

        self.word_experience_regex = re.compile(r'\w+\syears?', re.IGNORECASE)

        # Extract the academic qualifications
        self.academic_regex = re.compile(
            "(Master's | Bachelor's | Bachelor | Degree | National diploma | diploma | Certificate | O level | A level | Training | Experience | BSc)", re.IGNORECASE)

        # filename
        self.file = filename

        # year dict
        self.year_dict = {
            'one': 1, 'two': 2, 'three': 3,
            'four': 4, 'five': 5, 'six': 6,
            'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12,
            'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
            'nineteen': 19, 'twenty': 20
        }

        # Academic qualifications
        self.academic_qualifications = [
            'None',
            'National diploma',
            'Certificate',
            'O level',
            'Bachelor\'s degree',
            'A level',
            'Training/Experience',
            'Master\'s degree'
        ]

    def process_files(self):
        """starts the file processing and get the required fields from the job description

        Returns:
            _dict_: _Returns dictionary containing relevent fields to feed to the job description model_
            _str_: _Return string if the number of none values in the dictionary exceed 3 which would mean the template used might be the wrong one_
        """
        if self.file:
            self.extract_text()
            job_description_dict = {}

            job_description_dict["job_title"] = self.get_job_title()
            job_description_dict["purpose"] = self.get_purpose()
            job_description_dict["main_duties"] = self.get_main_duties()
            job_description_dict["experience"] = self.get_experience()
            job_description_dict["decisions_made"] = self.get_decisions_made(
            )
            job_description_dict["minimum_professional_qualification"] = self.get_minimum_profession_qualifications(
            )
            job_description_dict["academic_qualifications"] = self.get_academic_qualifications(
            )
            job_description_dict["planning_required"] = self.get_planning_required(
            )
            job_description_dict["technical_compentence"] = self.get_technical_competence_required(
            )

            none_count = 0
            for k, v in job_description_dict.items():
                if v == None:
                    none_count += 1

            if none_count >= 4:
                return "Too many values have failed to be identified, make sure your document is in the correct format"

            return job_description_dict

    def extract_text(self):
        """Extract the text from the file and save it to a text file
        """
        text = docx2txt.process(self.file)
        with open('temp_data.txt', 'w') as temp_file:
            temp_file.write(text)

        with open('temp_data.txt', 'r') as temp_file:
            self.file_lines = temp_file.readlines()

        # os.remove('temp_data.txt')

    def get_job_title(self):
        """Get the job title from the job description

        Returns:
            _str_: _job title from the job description_
            _None_: _If a match is not found_
        """
        for line in self.file_lines:
            line = line.split()
            line = " ".join(line)
            if self.job_title.findall(line.strip()) != []:
                user_job_title = line.split(':')[1].strip()
                return user_job_title

        return "None"

    def get_purpose(self):
        """Get the purpose from the job description

        Returns:
            _str_: _a string representing the overall purpose in the job description_
            _None_: _return none if no matches are found_
        """

        start = None
        end = None

        for line in self.file_lines:
            if 'overall job purpose' in line.lower() or 'overall purpose' in line.lower():
                start = self.file_lines.index(line)
            if 'main duties and responsibilities' in line.lower() or 'main duties & responsibilities' in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:
            overall_purpose = " ".join(self.file_lines[start+1:end])
            return overall_purpose.strip()
        return "None"

    def get_main_duties(self):
        """Get the main duties from the job description

        Returns:
            _str_: _a string representing the main duties in the job description_
        """

        start = None
        end = None

        for line in self.file_lines:
            if 'Main Duties and Responsibilities'.lower() in line.lower() or 'main duties & responsibilities' in line.lower():
                start = self.file_lines.index(line)
            if 'Supervision Received'.lower() in line.lower() or 'What decisions do you make'.lower() in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:

            main_duties = " ".join(self.file_lines[start+1:end])
            return main_duties.strip()

        return "None"

    def get_experience(self):
        """Gets the experience from the job description

        Returns:
            _int_: _Years of experience from the job description_
            _None_: _return none if no match is found_
        """

        for line in self.file_lines:

            num_regex = self.experience_regex.findall(line)

            if num_regex != []:
                xp_result = num_regex[0]
                experience = xp_result.split(" ")[0]
                return int(experience)

            try:
                word_regex = self.word_experience_regex.findall(line)
                if word_regex != []:
                    xp_result = word_regex[0]
                    experience = self.change_xp_words_to_num(
                        xp_result.split(" ")[0])
                    return experience
            except KeyError as e:
                pass

            month_regex = self.month_experience_regex.findall(line)
            if month_regex != []:
                xp_result = month_regex[0]
                experience = self.change_xp_month_to_year(
                    xp_result.split(" ")[0])
                return experience

            try:
                word_month_regex = self.word_month_xp_regex.findall(line)
                if word_month_regex != []:
                    xp_result = word_month_regex[0]
                    experience = self.change_xp_words_to_num(
                        xp_result.split(" ")[0])

                    experience = self.change_xp_month_to_year(experience)
                    return experience
            except KeyError:
                pass

        return "No Value detected."

    def change_xp_words_to_num(self, wrd):
        """Changes the experience specified on words to number

        Args:
            wrd (str): The value of the year or month as a number

        Returns:
            integer: Value of the the month or year
        """
        to_num_result = self.year_dict[wrd.lower()]
        return to_num_result

    def change_xp_month_to_year(self, mnth):
        """Change the experince in months to a fraction of a year

        Args:
            mnth (int): The value of the month

        Returns:
            float: value as a fraction of a year
        """
        to_year_result = int(mnth)/12
        return to_year_result

    def get_decisions_made(self):
        """Get the decions made from the job description aka key decisions

        Returns:
            _str_: _return a string representing the decisions made_
            _None_: _returns None if no match is found_
        """

        start = None
        end = None

        for line in self.file_lines:
            if 'decision making' in line.lower() or 'What decisions do you make'.lower() in line.lower():
                start = self.file_lines.index(line)
            if 'planning required' in line.lower() or 'Supervision Received'.lower() in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:
            decisions_made = " ".join(self.file_lines[start+1:end])
            return decisions_made.strip()

        return "None"

    def get_academic_qualifications(self):
        """_Get the academic qualification from the job description_

        Returns:
            _str_: _return a string representing the maximum qualifications required_
            __none_: _returns none if no match is found_
        """

        start = None
        end = None
        for line in self.file_lines:
            if 'academic qualification/training required' in line.lower() or 'Minimum academic qualifications required'.lower() in line.lower() or 'academic qualification and experience' in line.lower():
                start = self.file_lines.index(line)
            if 'critical or technical competencies required' in line.lower() or 'Minimum professional qualifications required'.lower() in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:
            ac_qualifications_result = " ".join(self.file_lines[start+1:end])
        if self.academic_regex.findall(ac_qualifications_result) != []:
            qualification = self.academic_regex.findall(
                ac_qualifications_result)[0].strip()
            if qualification.lower() in ['training', 'experience']:
                return 'Training/Experience'
            elif qualification.lower() in ["master's", "masters"]:
                return "Master's degree"
            elif qualification.lower() in ['degree', 'bachelor', "bachelor's", "bsc"]:
                return "Bachelor's degree"
            elif qualification.lower() in ['diploma', "national diploma"]:
                return "National diploma"

            elif qualification.lower() in ['certificate']:
                return "Certificate"

            return qualification

        return "None"

    def get_planning_required(self):
        """Get the planning required from the job description

        Returns:
            _str_: _returns a string representing the planning required in the job description_
        """
        start = None
        end = None

        for line in self.file_lines:
            if 'planning required' in line.lower():
                start = self.file_lines.index(line)
            if 'supervisory responsibility' in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:
            planning_rqred = " ".join(self.file_lines[start+1:end])
            return planning_rqred.strip()

        return "None"

    def get_technical_competence_required(self):
        """Get the technical competence required from the job description

        Returns:
            _str_: _returns a string representing the technical competence required in the job description_
        """

        start = None
        end = None

        for line in self.file_lines:
            if 'CRITICAL OR TECHNICAL COMPETENCIES REQUIRED'.lower() in line.lower() or 'Technical Skills'.lower() in line.lower():
                start = self.file_lines.index(line)
            if 'confirmation of job description' in line.lower() or 'CONFIRMATION OF JOB DESCRIPTION'.lower() in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:
            competence = " ".join(self.file_lines[start+1:end])
            return competence.strip()

        return "None"

    def get_minimum_profession_qualifications(self):
        """Get the minimum professional qualifications required from the job description

        Returns:
            _str_: _returns a string representing the minimum professional qualifications required in the job description_
        """

        start = None
        end = None

        for line in self.file_lines:
            if 'Academic Qualification and Experience'.lower() in line.lower() or 'Minimum professional qualifications required'.lower() in line.lower():
                start = self.file_lines.index(line)
            if 'Additional Training Required'.lower() in line.lower() or 'Experience required (in years)'.lower() in line.lower():
                end = self.file_lines.index(line)
                break

        if start and end:
            min_prof_requirements = " ".join(self.file_lines[start+1:end])
            return min_prof_requirements.strip()

        return "None"


# ExtractText('testing.docx')


# Required info
# Get the job title✅
# Purpose✅
# Main duties✅
# experience in years✅
# key decisions✅
# Planning required✅
# academic qualifications✅
# technical competence required✅
# minimum professional qualifications✅
