#!/usr/bin/env python

import unittest
import glob
import os
from val_description import CoeffSchemaDefinitions as coeffSchemaDefinitions
from val_description import CoeffCollectionDefinitions as coeffCollectionDefinitions
from lxml import etree as xmlParser
import lxml
import logging
import rospkg

classToActuatorCoeffFilenameDictionary = {'a': 'v_a_', 'b': 'v_b_', 'c': 'v_c_', 'd': 'v_d_', 'e': 'v_e_', 'f': 'v_f_', 'g': 'v_g_', 'h_athena1': 'athena1', 'h_athena2': 'athena2'}

classToActuatorSchemaDictionary = {'a': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'b': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'c': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'd': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'e': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'f': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'g': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'h_athena1': coeffSchemaDefinitions.athena1_actuator_coeffs_definition,
                                   'h_athena2': coeffSchemaDefinitions.athena2_actuator_coeffs_definition}

classToActuatorCoeffFilesSchemaDictionary = {'a': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'b': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'c': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'd': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'e': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'f': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'g': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'h_athena1': ''' ''',
                                             'h_athena2': ''' '''}


class coeffFileTests(unittest.TestCase):

    def setUp(self):
        rospack = rospkg.RosPack()

        self.catkinWorkspaceDirectory = rospack.get_path('val_description')

        # Define the directories that coeffs live in
        self.actuatorCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/actuators'
        self.classCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/class'
        self.controllerCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/controllers'
        self.locationCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/location'
        self.modesCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/modes'
        self.safetyCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/safety'
        self.sensorCoeffDirectory = self.catkinWorkspaceDirectory + '/instance/coefficients/sensors'

        self.log = logging.getLogger("Coeff Test Logger")
        self.correctFiles = []
        self.incorrectFiles = []

    def tearDown(self):
        pass

    def getSchemaParser(self, schema_definition):
        schema_root = xmlParser.XML(schema_definition)
        schema = xmlParser.XMLSchema(schema_root)
        return xmlParser.XMLParser(schema=schema)

    def checkForDuplicates(self, directory):
        # Assemble the schema
        os.chdir(directory)
        for coeffFile in glob.glob("*.xml"):
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                for coeff in xmlCoeffObject.iter('Coeff'):
                    coeffNames.append(coeff.get('id'))
                if len(coeffNames) != len(set(coeffNames)):
                    raise Exception
            except Exception:
                self.log.error(coeffFile + " has duplicate coeffs")
                self.incorrectFiles.append(coeffFile)
        assert len(self.incorrectFiles) == 0

    def checkSingleXmlId(self, classToCheck, expectedString, filenameString, xmlTagToCheck):
        os.chdir(self.actuatorCoeffDirectory)

        coeffFilesToCheck = []
        allCoeffFiles = glob.glob("*.xml")

        if filenameString is None or expectedString is None:
            return

        for coeffFile in allCoeffFiles:
            if filenameString in coeffFile:
                coeffFilesToCheck.append(coeffFile)

        if not coeffFilesToCheck:
            raise Exception("No filename found that match the string " + filenameString)

        for coeffFile in coeffFilesToCheck:
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                coeff = xmlCoeffObject.getroot().find(xmlTagToCheck).get('id')
                if not coeff == expectedString:
                    raise Exception
            except Exception:
                self.log.error(coeffFile + " has incorrect entry " + coeff + " for tag " + xmlTagToCheck)
                self.incorrectFiles.append(coeffFile)

        assert len(self.incorrectFiles) == 0

    def checkForNeededCoeffs(self, directory, classToCheck, neededCoeffs, filenameString, xmlTagToCheck='Coeff'):
        os.chdir(directory)

        coeffFilesToCheck = []
        allCoeffFiles = glob.glob("*.xml")

        if filenameString is None or not neededCoeffs:
            return

        for coeffFile in allCoeffFiles:
            if filenameString in coeffFile and 'test' not in coeffFile:  # Don't check test files
                coeffFilesToCheck.append(coeffFile)

        if not coeffFilesToCheck:
            raise Exception("No files found that match the string " + filenameString)

        for coeffFile in coeffFilesToCheck:
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                for coeff in xmlCoeffObject.iter(xmlTagToCheck):
                    coeffNames.append(coeff.get('id'))
                for coeff in neededCoeffs:
                    if coeff not in coeffNames:
                        raise Exception
            except Exception:
                self.log.error(coeffFile + " is missing a needed coeff " + coeff)
                self.incorrectFiles.append(coeffFile)
        assert len(self.incorrectFiles) == 0

    def checkValidSchema(self, schema, directory, filenameStringPatternToCheck):
        parser = self.getSchemaParser(schema)
        os.chdir(directory)

        if not filenameStringPatternToCheck is None:  # hacky way to skip some things.Giggity
            for coeffFile in glob.glob("*.xml"):
                if 'test' not in coeffFile and filenameStringPatternToCheck in coeffFile:
                    try:
                        root = xmlParser.parse(coeffFile, parser)
                        self.correctFiles.append(coeffFile)
                    except xmlParser.XMLSyntaxError:
                        self.log.error(coeffFile + " has coeffs that are not in the schema")
                        self.incorrectFiles.append(coeffFile)

        assert len(self.incorrectFiles) == 0

    ##################################################################################
    #  Check that actuator coeff files only have coeffs that should be in them.      #
    ##################################################################################
    def testActuatorCoeffsValidSchema(self):
        # Assemble the schema
        for classToCheck in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.safety_file_definitions + coeffSchemaDefinitions.sensor_files_definition + coeffSchemaDefinitions.location_files_definition + classToActuatorSchemaDictionary[classToCheck] + \
                coeffSchemaDefinitions.header_coeff_definition + classToActuatorCoeffFilesSchemaDictionary[classToCheck] + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.actuatorCoeffDirectory, classToActuatorCoeffFilenameDictionary[classToCheck])

    ###################################################################################
    #   Check that actuator coeff files have no duplicate coeffs.                     #
    ###################################################################################
    def testActuatorNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.actuatorCoeffDirectory)

    ####################################################################################
    #    Check that actuator coeff files have coeffs that need to be in them.          #
    ####################################################################################
    def testActuatorEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeededCoeffs(self.actuatorCoeffDirectory, classLetter, coeffCollectionDefinitions.ActuatorNeededCoeffs[classLetter], classToActuatorCoeffFilenameDictionary[classLetter])

    def testActuatorSensorFiles(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkSingleXmlId(classLetter, coeffCollectionDefinitions.AllowedSensorFiles[classLetter], classToActuatorCoeffFilenameDictionary[classLetter], 'SensorsFile')

    ####################################################################################
    #    Check that class coeff files only have coeffs that should be in them.         #
    ####################################################################################
    def testClassCoeffsValidSchema(self):
        # Assemble the schema
        for classToCheck in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.class_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.actuator_class_info_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.classCoeffDirectory, coeffCollectionDefinitions.AllowedClassFiles[classToCheck])

    ####################################################################################
    #    Check that class coeff files have no duplicate coeffs.                        #
    ####################################################################################
    def testClassNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.classCoeffDirectory)

    ####################################################################################
    #    Check that class coeff files have coeffs that need to be in them.             #
    ####################################################################################
    def testClassEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeededCoeffs(self.classCoeffDirectory, classLetter, coeffCollectionDefinitions.ClassNeededCoeffs[classLetter], coeffCollectionDefinitions.AllowedClassFiles[classLetter])

    ####################################################################################
    #    Check that controller coeff files only have coeffs that should be in them.    #
    ####################################################################################
    def testControllerCoeffsValidSchema(self):
        # Assemble the schema
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.controller_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            for controllerFile in coeffCollectionDefinitions.AllowedControllerFiles[classLetter]:
                self.checkValidSchema(schema, self.controllerCoeffDirectory, controllerFile)

    ####################################################################################
    #    Check that controller coeff files have no duplicate coeffs.                   #
    ####################################################################################
    def testControllerNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.controllerCoeffDirectory)

    ####################################################################################
    #    Check that controller coeff files have coeffs that need to be in them.        #
    ####################################################################################
    def testControllerEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            for filename in coeffCollectionDefinitions.AllowedControllerFiles[classLetter]:
                self.checkForNeededCoeffs(self.controllerCoeffDirectory, classLetter, coeffCollectionDefinitions.ControllerNeededCoeffs[classLetter], filename)

        ####################################################################################
        #    Check that location coeff files only have coeffs that should be in them.      #
        ####################################################################################
    def testLocationCoeffsValidSchema(self):
        # Assemble the schema
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.location_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            for locationFile in coeffCollectionDefinitions.AllowedLocationFiles[classLetter]:
                self.checkValidSchema(schema, self.locationCoeffDirectory, locationFile)

    ####################################################################################
    #    Check that location coeff files have no duplicate coeffs.                     #
    ####################################################################################
    def testLocationNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.locationCoeffDirectory)

    ####################################################################################
    #    Check that location coeff files have coeffs that need to be in them.          #
    ####################################################################################
    def testLocationEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            for filename in coeffCollectionDefinitions.AllowedLocationFiles[classLetter]:
                self.checkForNeededCoeffs(self.locationCoeffDirectory, classLetter, coeffCollectionDefinitions.LocationNeededCoeffs[classLetter], filename)

    ####################################################################################
    #    Check that safety coeff files only have coeffs that should be in them.        #
    ####################################################################################
    def testSafetyCoeffsValidSchema(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.safety_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.safetyCoeffDirectory, coeffCollectionDefinitions.AllowedSafetyFiles[classLetter])

    ####################################################################################
    #    Check that safety coeff files have no duplicate coeffs.                       #
    ####################################################################################
    def testSafetyNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.safetyCoeffDirectory)

    ####################################################################################
    #    Check that safety coeff files have coeffs that need to be in them.            #
    ####################################################################################
    def testSafetyEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeededCoeffs(self.safetyCoeffDirectory, classLetter, coeffCollectionDefinitions.SafetyNeededCoeffs, coeffCollectionDefinitions.AllowedSafetyFiles[classLetter])

    ####################################################################################
    #    Check that sensor coeff files only have coeffs that should be in them.        #
    ####################################################################################
    def testSensorCoeffsValidSchema(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.sensor_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.sensorCoeffDirectory, coeffCollectionDefinitions.AllowedSensorFiles[classLetter])

    ####################################################################################
    #    Check that sensor coeff files have no duplicate coeffs.                       #
    ####################################################################################
    def testSensorNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.sensorCoeffDirectory)

    ####################################################################################
    #    Check that sensor coeff files have coeffs that need to be in them.            #
    ####################################################################################
    def testSensorEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeededCoeffs(self.sensorCoeffDirectory, classLetter, coeffCollectionDefinitions.SensorNeededCoeffs, coeffCollectionDefinitions.AllowedSensorFiles[classLetter])
